from flask import Flask, Blueprint, render_template
from flask_restplus import Api, Resource
from flask_restplus import fields, reqparse

app = Flask(__name__)
api = Api(app = app)

app.config['UPLOAD_FOLDER'] = 'static/'

# Пространство имен
itask = api.namespace('individual_task', description='IT APIs')

# Модель book
book = api.model('book', {
    'book_name':fields.String,
    'author':fields.String,
    'genre':fields.String,
    'amount_of_volumes':fields.Integer,
    'amount_of_pages':fields.Integer
}, required = True, description = 'Book info')

# Модель minmax для поиска минимума и максимума
minmax = api.model('minmax', {
    'min':fields.String,
    'max':fields.String,
    'field':fields.String
}, required = True, description = 'Minimum and Maximum')

# Массивы
books = []
minmax_list = [0, 0, '']
same_genre = []

# Парсер add_book
add_book = reqparse.RequestParser()
add_book.add_argument('book_name', type=str, required=True)
add_book.add_argument('author', type=str, required=True)
add_book.add_argument('genre', type=str, required=True)
add_book.add_argument('amount_of_volumes', type=int, required=True)
add_book.add_argument('amount_of_pages', type=int, required=True)

# Парсер find_minmax
find_minmax = reqparse.RequestParser()
find_minmax.add_argument('field', type=str, required=True)

# Парсер remove
remove = reqparse.RequestParser()
remove.add_argument('book_name', type=str, required=True)

# Парсер sort
sort = reqparse.RequestParser()
sort.add_argument('field', type=str, required=True)

# Парсер upadte
update = reqparse.RequestParser()
update.add_argument('book_name', type=str, required=True)
update.add_argument('author', type=str, required=True)
update.add_argument('genre', type=str, required=True)
update.add_argument('amount_of_volumes', type=int, required=True)
update.add_argument('amount_of_pages', type=int, required=True)

# Парсер find_genre
find_genre = reqparse.RequestParser()
find_genre.add_argument('genre', type=str, required=True)

# Функции
# 1. Вывод
@itask.route('/')
class MainClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    def get(self):
        global books
        return books

# 2. Добавление
@itask.route('/add_book')
class AddElementClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    @itask.expect(add_book)
    def post(self):
        global books
        args = add_book.parse_args()
        index = 0
        isHere = False

        for i in books:
            if i['book_name'] == args['book_name'].lower():
                index = books.index(i)
                isHere = True

        if not isHere:
            books.append({
                'book_name': args['book_name'].lower(),
                'author': args['author'].lower(),
                'genre': args['genre'].lower(),
                'amount_of_volumes': args['amount_of_volumes'],
                'amount_of_pages': args['amount_of_pages']
            })
        else:
            books[index]['author'] = args['author'].lower()
            books[index]['genre'] = args['genre'].lower()
            books[index]['amount_of_volumes'] = args['amount_of_volumes']
            books[index]['amount_of_pages'] = args['amount_of_pages']

        return books

# 3. Удаление
@itask.route('/remove')
class RemoveClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    @itask.expect(remove)
    def delete(self):
        global books
        global same_genre
        args = remove.parse_args()

        for i in books:
            if i['book_name'] == args['book_name'].lower():
                del books[books.index(i)]
                if i in same_genre:
                    del same_genre[same_genre.index(i)]

        return books

# 4. Сортировка
@itask.route('/sort')
class SortClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    @itask.expect(sort)
    def put(self):
        global books
        args = sort.parse_args()

        try:
            books = sorted(books, key=lambda k: k[args['field'].lower()])
            return books
        except Exception:
            books = sorted(books, key=lambda k: k['book_name'].lower())
            return books

# 5. Обновление по указанному полю
@itask.route('/update_by_name')
class UpdateByNameClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    @itask.expect(update)
    def put(self):
        global books
        args = update.parse_args()

        for i in books:
            if i['book_name'] == args['book_name'].lower():
                books[books.index(i)]['author'] = args['author'].lower()
                books[books.index(i)]['genre'] = args['genre'].lower()
                books[books.index(i)]['amount_of_volumes'] = args['amount_of_volumes']
                books[books.index(i)]['amount_of_pages'] = args['amount_of_pages']

        return books

# 6. Поиск общих по жанру
@itask.route('/genres')
class FindGenreClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    @itask.expect(find_genre)
    def get(self):
        global same_genre
        global books
        args = find_genre.parse_args()

        same_genre = []

        for i in books:
            if (i not in same_genre) and (i['genre'] == args['genre']):
                same_genre.append(i)

        return same_genre

# 7. Поиск minmax
@itask.route('/minmax')
class MinmaxClass(Resource):
    @itask.doc("")
    @itask.marshal_with(minmax)
    @itask.expect(find_minmax)
    def get(self):
        global books
        global minmax_list
        args = find_minmax.parse_args()

        try:
            minmax_list[0] = books[0][args['field'].lower()]
            minmax_list[1] = 0
            minmax_list[2] = args['field'].lower()

            for i in books:
                if i[args['field'].lower()] > minmax_list[1]:
                    minmax_list[1] = i[args['field'].lower()]
                if i[args['field'].lower()] < minmax_list[0]:
                    minmax_list[0] = i[args['field'].lower()]

            return {'min':minmax_list[0], 'max':minmax_list[1], 'field':args['field'].lower()}
        except Exception:
            minmax_list[0] = books[0]['amount_of_pages']
            minmax_list[1] = 0
            minmax_list[2] = 'amount_of_pages'

            for i in books:
                if i['amount_of_pages'] > minmax_list[1]:
                    minmax_list[1] = i['amount_of_pages']
                if i['amount_of_pages'] < minmax_list[0]:
                    minmax_list[0] = i['amount_of_pages']

            return {'min':minmax_list[0], 'max':minmax_list[1], 'field':'amount_of_pages'}

# 8. Удаление по наименьшему количеству страниц
@itask.route('/remove/remove_by_the_lowest')
class RemoveTheLowestClass(Resource):
    @itask.doc("")
    @itask.marshal_with(book)
    def delete(self):
        global books
        global same_genre
        minimal = books[0]['amount_of_pages']
        index = 0
        index_genres = 0

        for i in books:
            if i['amount_of_pages'] < minimal:
                index = books.index(i)
                index_genres = same_genre.index(i)

        del books[index]
        if i in same_genre:
            del same_genre[index_genres]

        return books

# ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ
addtask = api.namespace('additional_task', description='ADD Task')

# Парсер changer
changer = reqparse.RequestParser()
changer.add_argument('book_name', type=str, required=True)
changer.add_argument('field', type=str, required=True)
changer.add_argument('value', type=str, required=True)

# Обновление по названию поля
@addtask.route('/update_by_name/update_by_field')
class UpdateByField(Resource):
    @addtask.doc("")
    @addtask.marshal_with(book)
    @addtask.expect(changer)
    def patch(self):
        global books
        global same_genre
        args = changer.parse_args()

        for i in books:
            if i['book_name'] == args['book_name'].lower():
                try:
                    if isinstance(i[args['field'].lower()], int):
                        i[args['field'].lower()] = int(args['value'])
                        same_genre[same_genre.index(i)][args['field'].lower()] = int(args['value'])
                    else:
                        i[args['field'].lower()] = args['value'].lower()
                        same_genre[same_genre.index(i)][args['field'].lower()] = args['value'].lower()
                except Exception:
                    print('An error has been occured!')

        return books

@app.route('/table', methods=["GET", "POST"])
def home():
    global books
    global same_genre
    global minmax_list

    return render_template('index.html', books = books, minmax = minmax_list, genres = same_genre)

if __name__  == '__main__':
    app.run(debug=True)
