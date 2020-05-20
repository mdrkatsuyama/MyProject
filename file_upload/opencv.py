import numpy as np
import cv2
import os
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from matplotlib import pyplot as plt
from pylab import rcParams #画像表示の大きさを変える
# %matplotlib inline
rcParams['figure.figsize'] = 25, 20  #画像表示の大きさ

"""pdfファイルをjpegに変換する"""
def change_filetype(request):
    # poppler/binを環境変数PATHに追加する
    poppler_dir = Path(__file__).parent.absolute() / "poppler/bin"
    os.environ["PATH"] += os.pathsep + str(poppler_dir)

    # PDFファイルのパス
    pdf_path = Path(request)

    # PDF -> Image に変換（150dpi）
    pages = convert_from_path(str(pdf_path), 150)

    # 画像ファイルを１ページずつ保存
    image_dir = Path("./media/documents/")
    for i, page in enumerate(pages):
        file_name = pdf_path.stem + "_{:02d}".format(i + 1) + ".jpeg"
        image_path = image_dir / file_name
        # JPEGで保存
        page.save(str(image_path), "JPEG")
        return file_name

"""画像の圧縮"""
def imgEncodeDecode(in_imgs, ch, quality=5):
    """
    入力された画像リストを圧縮する
    [in]  in_imgs:  入力画像リスト
    [in]  ch:       出力画像リストのチャンネル数 （OpenCV形式）
    [in]  quality:  圧縮する品質 (1-100)
    [out] out_imgs: 出力画像リスト
    """

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    out_imgs = []

    for img in in_imgs:
        result, encimg = cv2.imencode('.jpg', img, encode_param)
        if False == result:
            print('could not encode image!')
            exit()

        decimg = cv2.imdecode(encimg, ch)
        out_imgs.append(decimg)

    return out_imgs

def get_opencv(request):
    # 元データ
    src = request
    # 取り込んだ取り込んだデータがPDFか確認する
    if '.pdf' not in request :
        result = { "msg" : 'FileType Error' ,
               "src_jpeg" : '',
               "src_jpg" : '',
               "res_json" : {'result': 0, } }
        return result

    # 指定のディレクトリ
    image_dir = './media/documents/'
    filepath = image_dir + change_filetype(src);
    # 変換した画像を変数に格納
    img = cv2.imread(filepath, 0) # グレースケール
    # (1241, 1753) A4横向き, A4(1755, 1240) 縦向き
    # print(img.shape[0])

    edges = cv2.Canny(img, 1, 100, apertureSize=3)
    cv2.imwrite(image_dir + 'edges.png', edges)
    # 膨張処理
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel)

    # 輪郭抽出
    _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 面積でフィルタリング
    rects = []
    for cnt, hrchy in zip(contours, hierarchy[0]):
        if cv2.contourArea(cnt) < 30000:
            continue  # 面積が小さいものは除く
        if hrchy[3] == -1:
           continue  # ルートノードは除く
        # 輪郭を囲む長方形を計算する。
        rect = cv2.minAreaRect(cnt)
        rect_points = cv2.boxPoints(rect).astype(int)
        rects.append(rect_points)

    # x-y 順でソート
    rects = sorted(rects, key=lambda x: (x[0][1], x[0][0]))
    count = len(rects)
    if count == 0:
        result = {"msg": 'No Candidated Input Field!',
                  "src_jpeg": '',
                  "src_jpg": '',
                  "res_json": {'result': 0, }}
        return result


    # 描画する。
    # for i, rect in enumerate(rects):
    #     color = np.random.randint(0, 255, 3).tolist()
    #     cv2.drawContours(img, rects, i, color, 2)
    #     cv2.putText(img, str(i), tuple(rect[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 3)
    #
    #     print('rect:\n', rect)
    #
    # cv2.imwrite('img.png', img)

    # LEFT,RIGHT
    if rects[0][0][0] < rects[0][1][0]:
        left = rects[0][0][0]
        right = rects[0][1][0]
    elif rects[0][1][0] < rects[0][2][0]:
        left = rects[0][1][0]
        right = rects[0][2][0]
    elif rects[0][2][0] < rects[0][3][0]:
        left = rects[0][2][0]
        right = rects[0][3][0]

    # TOP, BOTTOM
    if rects[0][0][1] < rects[0][1][1]:
        top = rects[0][0][1]
        bottom = rects[0][1][1]
    elif rects[0][1][1] < rects[0][2][1]:
        top = rects[0][1][1]
        bottom = rects[0][2][1]
    elif rects[0][2][1] < rects[0][3][1]:
        top = rects[0][2][1]
        bottom = rects[0][3][1]

    height = bottom - top
    width = right - left
    # img[top : bottom, left : right] 東洋注文書仕様
    # サンプル1の切り出し、保存
    # img1 = grayed[275 : 545, 680: 1160]
    # img1 = img[280 : 550, 685: 1160]
    if height > width:
        height = right - left
        width = bottom - top
        img1 = img[top + 10: top + 10 + 441, left + 10: left + 10 + 236]
        img1 = np.rot90(img1)
    else:
        img1 = img[top + 10: top + 10 + 236, left + 10: left + 10 + 441]


    # 切り取られた四角のサイズを検証
    # print(height)
    # print(width)
    # (256, 461)
    if height > 280 or width > 500 or height < 230 or width < 430:
        # レスポンス
        result = {"msg": 'Data Format Error',
                  "src_jpeg": '',
                  "src_jpg": '',
                  "res_json": {"result":0,}}
        return result


    # img1 = img[top + 10 : bottom -10, left + 10 : right -10]
    # img1 = img[top + 10: top + 10 + 236, left + 10: left + 10 + 441]
    # (468, 259) 横向き (256, 461) 縦向き
    # (236, 441)
    print (top, left)
    print(rects)

    # 判定部位の画像の出力
    out_path = image_dir + 'out.jpg'
    cv2.imwrite(out_path, img1)
    # 判定する画像の読み込み
    img = cv2.imread(out_path)
    height, width, ch = img.shape

    # img = imgEncodeDecode(img, ch, quality=5);
    edges = cv2.Canny(img, 1, 100, apertureSize=3)
    cv2.imwrite(image_dir + 'edges2.png', edges)
    # 膨張処理
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel)

    # 輪郭抽出
    _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    # hierarchyが取得できたかどうかで判定する
    if hierarchy is None:
        msg = 'Error Data...'
        json = {"result": 0, }
    else:
        msg = 'Correct Data'
        json = {"result": 1, }

    # レスポンス
    result = { "msg" : msg ,
               "src_jpeg" : '../.' + filepath,
               "src_jpg" : '../../media/documents/out.jpg',
               "res_json" : json }

    return result