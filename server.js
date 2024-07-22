const express = require('express');
const fs = require('fs');
const cors = require('cors');
const app = express();

app.use(cors()); // Добавляем middleware для CORS
app.use(express.json()); // Добавляем поддержку JSON для тела запроса

let data = 0;
const dataFile = 'data.json';

// Функция для загрузки данных из файла
const loadData = () => {
    if (fs.existsSync(dataFile)) {
        const rawData = fs.readFileSync(dataFile);
        const parsedData = JSON.parse(rawData);
        data = parsedData.data || 0;
    }
};

// Функция для сохранения данных в файл
const saveData = () => {
    const dataToSave = { data };
    fs.writeFileSync(dataFile, JSON.stringify(dataToSave));
};

// Загружаем данные при запуске сервера
loadData();

// Функция для увеличения значения переменной data каждую секунду
setInterval(() => {
    if (data < 100) {
        data += 1;
        console.log(`Data incremented: ${data}`);
        saveData(); // Сохраняем данные в файл каждую секунду
    }
}, 1000);

// Маршрут для получения текущего значения переменной data
app.get('/data', (req, res) => {
    res.json({ data });
});

// Новый маршрут для установки нового значения переменной data
app.post('/data', (req, res) => {
    if (req.body && typeof req.body.data === 'number') {
        data = req.body.data;
        saveData(); // Сохраняем данные в файл
        res.status(200).send({ message: 'Data updated successfully' });
    } else {
        res.status(400).send({ message: 'Invalid data' });
    }
});

app.listen(port, () => {
    console.log(`Server is running `);
});