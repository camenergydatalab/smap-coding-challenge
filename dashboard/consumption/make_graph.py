import matplotlib.pyplot as plt
import base64
from io import BytesIO


# プロットしたグラフを画像データとして出力するための関数
def Output_Graph():
    # バイナリI/O(画像や音声データを取り扱う際に利用)
    buffer = BytesIO()
    # png形式の画像データを取り扱う
    plt.savefig(buffer, format="png")
    # ストリーム先頭のoffset byteに変更
    buffer.seek(0)
    # バッファの全内容を含むbytes
    img = buffer.getvalue()
    # 画像ファイルをbase64でエンコード
    graph = base64.b64encode(img)
    # デコードして文字列から画像に変換
    graph = graph.decode("utf-8")
    buffer.close()

    return graph


# グラフをプロットするための関数
def Plot_Graph(x, y, x_label=None, y_label=None, type=1):
    # スクリプトを出力させない
    plt.switch_backend("AGG")
    # グラフサイズ
    plt.figure(figsize=(10, 5))

    if type == 1:
        # 折れ線グラフ作成
        plt.plot(x, y, marker='.', markersize=15)
        # xラベル
        plt.xlabel(x_label)
        # yラベル
        plt.ylabel(y_label)
        # X軸値を45度傾けて表示
        plt.xticks(rotation=45)
    else:
        # 円グラフの作成
        plt.pie(x, startangle=90, autopct="%1.1f%%", labels=y)

    # レイアウト
    plt.tight_layout()
    # グラフプロット
    graph = Output_Graph()

    return graph
