import win32print
import win32ui
from PIL import Image, ImageWin
from flask import Flask,request
from flask_cors import CORS
import base64
import io

HORZRES = 8
VERTRES = 10

PHYSICALWIDTH = 110
PHYSICALHEIGHT = 111

#这个服务需要在安装了打印机的电脑运行，自行添加修改自己的打印机名称


def printImg(fileStream,printType):

    # 小票
    if (printType == 'XP' or printType == 'ZYD' or printType == 'YXD' 
        or printType == 'WCLQD' or printType == 'CXZYD'  or printType == 'FKZLD'): 
        printerName = 'XP-80C' # 直连的打印机
    # 检验条形码 可能需要设置打印机首选项的纸张大小
    elif printType == 'JY':
        printerName = r'\\192.168.1.111\TSC TTP-244 Pro'  # 别人共享的打印机
    elif printType == 'FP':
        printerName = r'\\192.168.1.111\HP LaserJet 1020'  

    hDC = win32ui.CreateDC ()
    hDC.CreatePrinterDC (printerName)
    printable_area = hDC.GetDeviceCaps (HORZRES), hDC.GetDeviceCaps (VERTRES)
    bmp = Image.open (fileStream)
    # if bmp.size[0] > bmp.size[1]:
    #  bmp = bmp.rotate (90)
    
    ratios = [1.0 * printable_area[0] / bmp.size[0], 1.0 * printable_area[1] / bmp.size[1]]
    scale = min (ratios)
    
    print(printable_area)
    print(bmp.size)

    hDC.StartDoc ('自助机打印')
    hDC.StartPage ()

    dib = ImageWin.Dib (bmp)
    scaled_width, scaled_height = [int (scale * i) for i in bmp.size]
    x1 = int ((printable_area[0] - scaled_width) / 2)
    y1 = int ((printable_area[1] - scaled_height) / 2)
    x2 = x1 + scaled_width
    y2 = y1 + scaled_height
    # dib.draw (hDC.GetHandleOutput (), (x1, y1, x2, y2))
    if (printType == 'XP' or printType == 'ZYD' or printType == 'YXD' 
        or printType == 'WCLQD' or printType == 'CXZYD' or printType == 'FKZLD'):
        dib.draw (hDC.GetHandleOutput (), (x1, 0, x2, scaled_height))
    elif printType == 'JY' :
        dib.draw (hDC.GetHandleOutput (), (0, 0, 440, 232))
    elif printType == 'FP':
        dib.draw (hDC.GetHandleOutput (), (x1, 0, x2, scaled_height))
    
    hDC.EndPage ()
    hDC.EndDoc ()
    hDC.DeleteDC ()


app = Flask(__name__)
# 可能需要禁用浏览器的Block insecure private network requests才能跨域请求.
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
# CORS(app)

@app.route('/print', methods=['POST'])
def print_image():
    data = request.json
    image_data = data['image']
    printType = data['type']
    if image_data:
        header,encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image_stream = io.BytesIO(image_bytes)
        printImg(image_stream,printType)
        return "success"
    else:
        return "error"
    

if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1',port=15588)

