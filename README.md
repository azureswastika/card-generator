# Card generator

## Установка

```bash
git clone https://github.com/azureswastika/photo-generator.git # или скачать архив
...
pip install -r requirements.txt
```

## Запуск

```bash
python app.py # или запустить файл start.bat
```

## При ошибке "flask_uploads: ImportError"

```py
# Файл - env/Lib/site-packeges/flask_uploads.py
...
from werkzeug import secure_filename,FileStorage
...
```

заменить на

```py
# Файл - env/Lib/site-packeges/flask_uploads.py
...
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
...
```
