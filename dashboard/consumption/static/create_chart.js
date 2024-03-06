// テンプレート変数の取得
const elementWithData = document.getElementById('data');
const weekdayList = JSON.parse(elementWithData.getAttribute('data-weekdayList'));
const holidayList = JSON.parse(elementWithData.getAttribute('data-holidayList'));

// グラフで使用する色の配列
const backgroundColorArray = [
    'rgba(0, 123, 255, 0.5)',
    'rgba(255, 99, 132, 0.5)',
    'rgba(23, 162, 184, 1)',
    'rgba(255, 193, 7, 1)'
]
const borderColorArray = [
    'rgba(0, 123, 255, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(23, 162, 184, 1)',
    'rgba(255, 193, 7, 1)'
]
const hoverBackgroundColorArray =[
    'rgba(0, 123, 255, 0.7)',
    'rgba(255, 99, 132, 0.7)',
    'rgba(23, 162, 184, 0.7)',
    'rgba(255, 193, 7, 0.7)'
]
const hoverBorderColorArray = [
    'rgba(222, 35, 65, 242)',
    'rgba(255, 99, 132, 1)',
    'rgba(23, 162, 184, 1)',
    'rgba(255, 193, 7, 1)'
]

// データセットの作成処理
function createDataset(dayList, i) {
    dataset = []
    for (let i=0; i < dayList.length; i++) {
        value = Object.values(dayList[i])[0],
        console.log(value)
        area_data = {
            label: Object.keys(dayList[i])[0],
            backgroundColor: backgroundColorArray[i],
            borderColor: borderColorArray[i],
            hoverBackgroundColor: hoverBackgroundColorArray[i],
            hoverBorderColor: hoverBorderColorArray[i],
            data: [value.late_night, value.morning, value.evening, value.daytime, value.night]
        };
        dataset.push(area_data)
    }
    return dataset
}

const weekdayDataset = createDataset(weekdayList)
const holidayDataset = createDataset(holidayList)

const options = {
responsive: true,
maintainAspectRatio: false,
plugins: {
    title: {
    display: true,
    font: {
        size: 18
    }
    }
}
};

const weekdayOptions = {
...options,
plugins: {
    title: {
    ...options.plugins.title,
    text: '平日'
    }
}
};

const holidayOptions = {
...options,
plugins: {
    title: {
    ...options.plugins.title,
    text: '休日'
    }
}
};

const labels = [
    '深夜',
    '朝',
    '昼',
    '夕方',
    '夜',
]
const weekdayChart = document.getElementById('weekdayChart').getContext('2d');
new Chart(weekdayChart, {
type: 'bar',
data: { labels: labels, datasets: weekdayDataset},
options: weekdayOptions
});

const holidayChart = document.getElementById('holidayChart').getContext('2d');
new Chart(holidayChart, {
type: 'bar',
data: { labels: labels, datasets: holidayDataset },
options: holidayOptions
});