from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	path('plantilla/', views.plantilla, name='plantilla'),
	path('add-wiki/', views.addwiki, name='addwiki'),
	path('edit-wiki/<wikiid>', views.editwiki, name='editwiki'),
	path('wiki/<wid>', views.wiki, name='wiki'),
	path('', views.homepage, name='homepage'),
	path('add-book/', views.addbook, name='addbook'),
	path('book/<bookid>', views.book, name='book'),
	path('books/', views.books, name='books'),
	path('bqueue/', views.bqueue, name='bqueue'),
	path('bunko/', views.bunko, name='bunko'),
	path('bkqueue/', views.bkqueue, name='bkqueue'),
	path('readbook/', views.readbook, name='readbook'),
	path('appendwiki/', views.appendwiki, name='appendwiki'),
	path('page/<p>', views.pagina, name='page'),
	path('add-movie/', views.addmovie, name='addmovie'),
	path('movie/<movieid>', views.movie, name='movie'),
	path('watchmovie/', views.watchmovie, name='watchmovie'),
	path('movies/', views.movies, name='movies'),
	path('mqueue/', views.mqueue, name='mqueue'),
	path('add-show/', views.addshow, name='addshow'),
	path('show/<show_id>', views.show, name='show'),
	path('watchshow/', views.watchshow, name='watchshow'),
	path('addnewseason/', views.addnewseason, name='addnewseason'),
	path('shows/', views.shows, name='shows'),
	path('showqueue/', views.showqueue, name='showqueue'),
	path('addnewrelwiki/', views.addnewrelwiki, name='addnewrelwiki'),
	path('itemcol/<itm>/<col>', views.itemcol, name='itemcol'),
	path('fastedit/', views.fastedit, name='fastedit'),
	path('addbooktolist/', views.addbooktolist, name='addbooktolist'),
	path('booklists/', views.booklists, name='booklists'),
	path('booklist/<lid>', views.booklist, name='booklist'),
	path('addprogressbar/', views.addprogressbar, name='addprogressbar'),
	path('saveprogress/', views.saveprogress, name='saveprogress'),
	path('statistics/', views.statistics, name='statistics'),
	path('search/', views.busqueda, name='search'),
	path('kindlePublish/<p>', views.htmlPublish, name='kindlePublish'),
	path('saveshowprogress/', views.saveshowprogress, name='saveshowprogress'),
	path('addbookmedia/', views.addbookmedia, name='addbookmedia'),


	]