/**
 * 名前 : display_line_chart
 * 処理 : chart.jsを用いて、折れ線グラフを生成、描画する
 * 引数 : 
 *      element_id : 折れ線グラフを描画するcanvasタグの要素オブジェクト
 *      chart_data_json : Chartクラスのdataに渡すJSONデータ
 */

function display_line_chart(ctx, chart_data_json) {

    new Chart(ctx, {
        type: 'line',
        data: chart_data_json,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

}