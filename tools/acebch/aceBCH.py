import struct
import subprocess
import sys
import os
from PIL import Image


def runCMD(cmd):
    with open(os.devnull, "wb") as devnull:
        subprocess.check_call(cmd, stdout=devnull, stderr=subprocess.STDOUT)


def readu32(inF):
    return struct.unpack("<I", inF.read(4))[0]


def readu16(inF):
    return struct.unpack("<H", inF.read(2))[0]


def readu8(inF):
    return struct.unpack("<B", inF.read(1))[0]


def writeu32(inF, what):
    inF.write(struct.pack("<I", what))


def writeu16(inF, what):
    inF.write(struct.pack("<H", what))


def writeu8(inF, what):
    inF.write(struct.pack("<B", what))


def doHelp():
    print("aceBCH.py [mode] [input] [optional: output]")
    print("modes:")
    print("\t-e\t\textract, convert to PNG")
#    print("\t-i\t\tinsert from PNG")
    print("\n")
    print("optional:")
    print("\toutput\t\tspecify output file name")


def getPixel(data, x, y, imgW):
    i = ((y * imgW) + x) * 4
    # this is pure laziness right here...
    tmpR = ord(data[i])
    tmpG = ord(data[i + 1])
    tmpB = ord(data[i + 2])
    tmpA = ord(data[i + 3])
    return (tmpR, tmpG, tmpB, tmpA)


def makePNG(data, imgH, imgW, fileName):
    tmpImg = Image.new("RGBA", (imgW, imgH))
    for y in range(imgH):
        for x in range(imgW):
            tmpImg.putpixel((x, y), getPixel(data, x, y, imgW))

    tmpImg.save(fileName)


def calcImgDataSize(fmt, h, w):
    if(fmt == 0xc):
        return ((h * w) / 2)
    elif(fmt == 0xd):
        return (h * w)
    else:
        raise ValueError("UNSUPPORTED IMAGE FORMAT: {}".format(hex(fmt)))


def readPixelRGB565(inP):
    tmpCol = readu16(inP)
    r5 = (tmpCol & 0xf800) >> 11
    g6 = (tmpCol & 0x7e0) >> 5
    b5 = (tmpCol & 0x1f)

    r8 = (r5 << 3) | (r5 >> 2)
    g8 = (g6 << 2) | (g6 >> 4)
    b8 = (b5 << 3) | (b5 >> 2)
    return (r8, g8, b8, 0xff)
    #return (((tmpCol>>11)&0x1f)*8,((tmpCol>>5)&0x3f)*4,((tmpCol)&0x1f)*8,0xff)


def parseTile(tmpImg, x, y, fmt, inputFile):
    tileOrder = [0, 1, 8, 9, 2, 3, 10, 11, 16, 17, 24, 25, 18, 19, 26, 27, 4,
                 5, 12, 13, 6, 7, 14, 15, 20, 21, 28, 29, 22, 23, 30, 31, 32,
                 33, 40, 41, 34, 35, 42, 43, 48, 49, 56, 57, 50, 51, 58, 59,
                 36, 37, 44, 45, 38, 39, 46, 47, 52, 53, 60, 61, 54, 55, 62,
                 63]
    pixelFuncts = {0x3: readPixelRGB565}
    for k in range(8 * 8):
        i = tileOrder[k] % 8
        j = int((tileOrder[k] - i) / 8)

        pixel = pixelFuncts[fmt](inputFile)
        tmpImg.putpixel((y + j, x + i), pixel)


def decodeStdFmt(w, h, fmt, imgName, inputFile):
    print('hi')
    tmpImg = Image.new("RGBA", (w, h))
    validFmts = [0x3]
    if(fmt in validFmts):
        for j in range(0, h, 8):
            for k in range(0, w, 8):
                parseTile(tmpImg, k, j, fmt, inputFile)

    tmpImg.save(imgName)


def unBCH(fName, outName):
    inP = open(fName, "rb")
    if(inP.read(4) != b"BCH\x00"):
        print("FILE IS NOT A BCH FILE!")
        return 0

    print("Extracting {} as {}...".format(fName, outName))
    inP.seek(0x10)
    imgInfoOffset = readu32(inP)
    imgDataOffset = readu32(inP)

    # get imageInfo...
    inP.seek(imgInfoOffset)
    imgH = readu16(inP)
    imgW = readu16(inP)
    inP.read(0x14)
    imgFmt = readu16(inP)

    inP.seek(imgDataOffset)

    lazyFmt = {0xc: "-etc1", 0xd: '-etc1a4'}
    print(imgFmt)
    if(imgFmt in lazyFmt):
        imgDataSize = calcImgDataSize(imgFmt, imgH, imgW)
        imgData = inP.read(imgDataSize)
        outP = open(fName + ".pix", "wb")
        outP.write(imgData)
        outP.close()

        tmpCmd = "etc1Util -d {} {}.pix {} {}".format(lazyFmt[imgFmt],
                                                      fName, imgW, imgH)
        print(tmpCmd)
        runCMD(tmpCmd)

        imgData = open("{}.pix.data".format(fName), "rb")
        imgRawData = imgData.read()
        imgData.close()

        if(os.path.exists("{}.pix".format(fName))):
            os.remove("{}.pix".format(fName))
        if(os.path.exists("{}.pix.data".format(fName))):
            os.remove("{}.pix.data".format(fName))

        makePNG(imgRawData, imgH, imgW, outName)
    elif(imgFmt == 0x3):
        decodeStdFmt(imgW, imgH, imgFmt, outName, inP)
    # return 0


def reBCH(fName, outName):
    return 0


def main():
    # print(sys.argv)
    if(len(sys.argv) < 3):
        doHelp()
        return 0

    inName = sys.argv[2]
    outName = inName.split(".")[0]

    if(len(sys.argv) == 4):
        outName = sys.argv[3]
    # print outName
    if(sys.argv[1] == '-e'):
        outName += ".png"
        unBCH(inName, outName)
    # elif(sys.argv[1] == '-i'):
    #    outName += '.bch'
    #    reBCH(inName,outName)
    else:
        print("UNKNWON MODE: {}".format(sys.argv[1]))


if __name__ == '__main__':
    main()
