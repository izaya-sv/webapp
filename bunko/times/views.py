from django.shortcuts import render, redirect
from django import template
from .models import *
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, Max
from django.db.models import FloatField
from django.db.models import F
from django.db.models.functions import Round
from django.db.models.functions import Cast
from datetime import datetime
import math


def plantilla(request):
	return render(request,'base_forms.html',{})

def busqueda(request):
	keyword = request.POST.get("kw")

	if len(keyword)>2:
		wiki_matches = Wiki.objects.filter(Q(title__contains=keyword) | Q(info__contains=keyword)).order_by('updated_at')
		book_matches = Book.objects.filter(Q(title__contains=keyword) | Q(info__contains=keyword))
		movie_matches = Movie.objects.filter(Q(title__contains=keyword) | Q(info__contains=keyword))

	return render(request,'results.html',{'wikies':wiki_matches,'books':book_matches,'movies':movie_matches,'keyword':keyword})


def addwiki(request):
	wtypes = WikiType.objects.all().order_by('category')

	if request.method == 'POST':
		this_cat = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
		this_titulo = request.POST.get("title")
		this_info = request.POST.get("info")

		newW = Wiki.objects.create(wtype=this_cat,title=this_titulo,info=this_info,updated_at=datetime.now())
		newW.save()

		return redirect('/wiki/{}'.format(newW.id))
	else:
		return render(request,'add-wiki.html',{'wtypes':wtypes})

def editwiki(request,wikiid):
	this_wiki = Wiki.objects.get(pk=int(wikiid))
	wtypes = WikiType.objects.all()

	if request.method == 'POST':
		this_cat = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
		this_titulo = request.POST.get("title")
		this_info = request.POST.get("info")
		Wiki.objects.filter(id=int(wikiid)).update(wtype=this_cat,title=this_titulo,info=this_info,updated_at=datetime.now())

		return redirect('/wiki/{}'.format(this_wiki.id))
	else:
		return render(request,'edit-wiki.html',{'this_wiki':this_wiki,'wtypes':wtypes})

def fastedit(request):
	this_cat = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
	this_titulo = request.POST.get("title")
	this_info = request.POST.get("info")
	Wiki.objects.filter(id=int(request.POST.get("wikiid"))).update(wtype=this_cat,title=this_titulo,info=this_info,updated_at=datetime.now())
	if request.POST.get("origen")=='wiki_1':
		return redirect('/wiki/{}'.format(request.POST.get("wikiid")))
	else:
		return redirect('/itemcol/{}/{}'.format(request.POST.get("wikiid"),request.POST.get("colid")))



def wiki(request,wid):
	this_wiki = Wiki.objects.get(pk=int(wid))
	collection = Pagina.objects.all().order_by('titulo')
	wtypes = WikiType.objects.all()

	rel_books = Book.objects.raw("""
		select
		    a.*
		from
		    times_book a
		    inner join times_credito b
		    on a.id = b.media_id
		    inner join times_wiki c
		    on b.persona_id = c.id
		where
		    c.id = {}
		   order by a.pub_year
		    """.format(this_wiki.id))

	return render(request,'view-wiki.html',{'this_wiki':this_wiki,'paginas':collection,'wtypes':wtypes,'creditos':rel_books})

def homepage(request):
	nlist = 16
	npics = Wiki.objects.all().count()
	npages = math.ceil(npics/nlist)
	articles = Wiki.objects.all().exclude(wtype__id=1).exclude(id=42).order_by('-updated_at')[0:nlist]
	pinned_posts = Wiki.objects.filter(id=42)
	on_reading = ProgressBar.objects.filter(avance__lt=F('cantidad'))
	now_watching = SeasonProgressBar.objects.filter(avance__lt=F('temporada__episodes'))

	authors = Credito.objects.filter(ctype__id=1,media_type=1).exclude(persona__id__in = [36,40]).values('persona__title','persona__id').annotate(qbooks=Count('media_id')).order_by('-qbooks')

	dpaginas = PageRels.objects.values('page__titulo','page__id').annotate(qitems = Count('page__id'), lastup=Max('child__updated_at')).order_by('-lastup')[0:50]

	return render(request,'homepage.html',{'articles':articles,'pinned_posts':pinned_posts,'dpaginas':dpaginas,'npages':range(npages),'on_reading':on_reading,'now_watching':now_watching	,'authors':authors})

def addbook(request):
	personas = Wiki.objects.filter(wtype__category='persona').order_by('title')
	booktypes = WikiType.objects.filter(id__in=[9,10,11,12]).order_by('id')

	if request.method == 'POST':
		autor = Wiki.objects.get(pk=int(request.POST.get("autor")))
		btype = WikiType.objects.get(pk=int(request.POST.get("btype")))
		btitle = request.POST.get("title")
		binfo = request.POST.get("info")
		pubyear = int(request.POST.get("pub_year"))
		origlan = request.POST.get("orig_lan")

		newB = Book.objects.create(title = btitle,orig_lan = origlan,info=binfo, pub_year=pubyear, wtype=btype)
		newB.save()
		if btype.id == 9:
		    credtype = CreditType.objects.get(pk=1)
		elif btype.id == 10:
		    credtype = CreditType.objects.get(pk=7)
		elif btype.id == 11:
		    credtype = CreditType.objects.get(pk=5)
		elif btype.id == 12:
		    credtype = CreditType.objects.get(pk=6)

		newC = Credito.objects.create(ctype=credtype, persona = autor, media_type=1, media_id=newB.id)

		return redirect('/book/{}'.format(newB.id))
	else:
		return render(request,'add-book.html',{'personas':personas,'booktypes':booktypes})

def book(request,bookid):
	this_book = Book.objects.get(pk=int(bookid))
	wtypes = WikiType.objects.all()
	related_wikis = MediaWiki.objects.filter(media_type=1, media_id=this_book.id).order_by('-id')
	listas = BookList.objects.all().order_by('listname')

	barras = ProgressBar.objects.filter(libro=this_book,avance__lt=F('cantidad'))

	return render(request,'view-book.html',{'this_book':this_book,'wtypes':wtypes,'relw':related_wikis,'blistas':listas,'barras':barras})

def books(request):

	rqueue = Book.objects.filter(consumo__volume__isnull=True, wtype__id=9).order_by('pub_year')
	rhist = Consumo.objects.filter(volume__wtype__id=9).order_by('-finish_d','-id')

	return render(request,'books.html',{'rhist':rhist,'rqueue':rqueue})

def bqueue(request):

	rqueue = Book.objects.filter(consumo__volume__isnull=True, wtype__id=9).order_by('pub_year')
	rhist = Consumo.objects.all().order_by('-finish_d')

	return render(request,'bqueue.html',{'rhist':rhist,'rqueue':rqueue})

def bunko(request):

	rqueue = Book.objects.filter(consumo__volume__isnull=True, wtype__id__in=[10,11,12]).order_by('pub_year')
	rhist = Consumo.objects.filter(volume__wtype__id__in=[10,11,12]).order_by('-finish_d')

	return render(request,'bunko.html',{'rhist':rhist,'rqueue':rqueue})

def bkqueue(request):

	rqueue = Book.objects.filter(consumo__volume__isnull=True, wtype__id__in=[10,11,12]).order_by('pub_year')
	rhist = Consumo.objects.all().order_by('-finish_d')

	return render(request,'bkqueue.html',{'rhist':rhist,'rqueue':rqueue})

def readbook(request):
	rbook = Book.objects.get(pk=int(request.POST.get("bookid")))

	fecha_i = request.POST.get("start_d")
	fecha_f = request.POST.get("finish_d")
	bpages = request.POST.get("pages")

	newR = Consumo.objects.create(volume = rbook, pages=bpages,start_d=fecha_i,finish_d=fecha_f)
	newR.save()

	return redirect('/book/{}'.format(rbook.id))

def appendwiki(request):
	this_wiki = Wiki.objects.get(pk=int(request.POST.get("wikiid")))
	this_page = Pagina.objects.get(pk=int(request.POST.get("pageid")))

	newR = PageRels.objects.create(page=this_page, child=this_wiki)
	newR.save()

	return redirect('/wiki/{}'.format(this_wiki.id))

def pagina(request,p):
	this_page = Pagina.objects.get(pk=int(p))
	children = PageRels.objects.filter(page=this_page).order_by('-child__updated_at')

	return render(request,'page.html',{'this_page':this_page,'children':children})

def htmlPublish(request,p):
	this_page = Pagina.objects.get(pk=int(p))
	children = PageRels.objects.filter(page=this_page).order_by('child__id')

	return render(request,'kindlePublish.html',{'this_page':this_page,'children':children})

def addmovie(request):
	if request.method == 'POST':
		mtitle = request.POST.get("title")
		mpremiere = request.POST.get("premiere")
		mruntime = request.POST.get("runtime")
		minfo = request.POST.get("info")

		newM = Movie.objects.create(title=mtitle,premiere=mpremiere,runtime=mruntime,info=minfo)
		newM.save()
		return redirect('/movie/{}'.format(newM.id))
	else:
		return render(request,'add-movie.html',{})

def movie(request,movieid):
	this_movie = Movie.objects.get(pk=int(movieid))
	wtypes = WikiType.objects.all()
	related_wikis = MediaWiki.objects.filter(media_type=2, media_id=this_movie.id).order_by('-id')
	return render(request,'view-movie.html',{'this_movie':this_movie,'wtypes':wtypes,'relw':related_wikis})

def watchmovie(request):
	wmovie = Movie.objects.get(pk=int(request.POST.get("movieid")))

	fecha_i = request.POST.get("start_d")

	newR = MovieWatch.objects.create(film=wmovie,wdate=fecha_i)
	newR.save()

	return redirect('/movie/{}'.format(wmovie.id))

def movies(request):
	wmovies = MovieWatch.objects.all().order_by('-wdate')
	return render(request,'movies.html',{'wmovies':wmovies})

def mqueue(request):
	twmovies = Movie.objects.filter(moviewatch__film__isnull=True).order_by('premiere')
	return render(request,'mqueue.html',{'twmovies':twmovies})

def addshow(request):
	if request.method == 'POST':
		stitle = request.POST.get("title")
		stype = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
		sinfo = request.POST.get("info")
		spremiere = request.POST.get("premiere")
		sepisodes= request.POST.get("episodes")
		avgdur = request.POST.get("avgduration")

		newSH = Show.objects.create(title=stitle,info=sinfo,wtype=stype)
		newSH.save()

		newSE = Season.objects.create(show=newSH,season_t='S1',info = sinfo, episodes=sepisodes, avg_runtime=avgdur,premiere=spremiere)
		newSE.save()

		return redirect('/show/{}'.format(newSH.id))
	else:
		showtypes = WikiType.objects.filter(id__in=[14,15]).order_by('id')
		return render(request,'add-show.html',{'showtypes':showtypes})

def show(request,show_id):
	this_show = Show.objects.get(pk=int(show_id))
	this_seasons = Season.objects.filter(show=this_show)
	wtypes = WikiType.objects.all()

	related_wikis = MediaWiki.objects.filter(media_type=3, media_id=this_show.id).order_by('-id')

	return render(request,'view-show.html',{'this_show':this_show,'this_seasons':this_seasons,'wtypes':wtypes,'relw':related_wikis})

def watchshow(request):
	this_season = Season.objects.get(pk=int(request.POST.get("seasonid")))
	inicio = request.POST.get("start_d")
	fin = request.POST.get("finish_d")

	newW = SeasonProgressBar.objects.create(temporada=this_season,avance=1,fecha_inicio=inicio)
	newW.save()

	newPA = SeasonProgressLog.objects.create(barra=newW, fecha=inicio, progreso=1, delta_lec=1)
	newPA.save()

	return redirect('/show/{}'.format(this_season.show.id))

def addnewseason(request):
	this_show = Show.objects.get(pk=int(request.POST.get("show_id")))
	stitle = request.POST.get("stitle")
	sinfo = request.POST.get("info")
	spremiere = request.POST.get("premiere")
	sepisodes= request.POST.get("episodes")
	avgdur = request.POST.get("avgduration")

	newSE = Season.objects.create(show=this_show,season_t=stitle,info = sinfo, episodes=sepisodes, avg_runtime=avgdur,premiere=spremiere)
	newSE.save()

	return redirect('/show/{}'.format(this_show.id))

def shows(request):
	watchedshows = ShowWatch.objects.all().order_by('-finish_d')
	return render(request,'shows.html',{'watchedshows':watchedshows})

def showqueue(request):
	twshows = Show.objects.all().order_by('title')
	return render(request,'showqueue.html',{'twshows':twshows})

def addnewrelwiki(request):
	this_cat = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
	this_titulo = request.POST.get("title")
	this_info = request.POST.get("info")
	newW = Wiki.objects.create(wtype=this_cat,title=this_titulo,info=this_info,updated_at=datetime.now())
	newW.save()

	newRW = MediaWiki.objects.create(mwiki=newW,media_type=int(request.POST.get("media_type")), media_id=int(request.POST.get("media_id")))
	newRW.save()

	return redirect('/')

def itemcol(request,itm,col):
	this_wiki = Wiki.objects.get(pk=int(itm))
	collection = Pagina.objects.get(pk=int(col))
	all_items = PageRels.objects.filter(page=collection).exclude(child=this_wiki).order_by('child__title')
	wtypes = WikiType.objects.all()
	collections = Pagina.objects.all()
	return render(request,'view-wiki-cols.html',{'this_wiki':this_wiki,'pagina':collection,'all_items':all_items,'paginas':collections,'wtypes':wtypes})

def addbooktolist(request):
	lista_id = request.POST.get("lista_id")
	book_id = request.POST.get("book_id")
	this_lista = BookList.objects.get(pk=int(lista_id))
	this_book  = Book.objects.get(pk=int(book_id))

	newR = RelBookList.objects.create(blist=this_lista,bbook=this_book)
	newR.save()

	return redirect('/booklist/{}'.format(lista_id))

def booklists(request):
	listas = BookList.objects.raw("""
                select
                a.*
                from
                times_booklist a
                left join (
                select
                    a.blist_id,
                    max(c.finish_d) max_f
                from
                    times_relbooklist a
                    inner join times_book b
                    on a.bbook_id = b.id
                    inner join times_consumo c
                    on b.id = volume_id
                group by
                    a.blist_id ) b
                on a.id = b.blist_id
                order by
                ifnull(b.max_f,'1999-12-31') desc, a.id desc
	""")
	return render(request,'booklists.html',{'listas':listas})


def booklist(request,lid):
	this_lista = BookList.objects.get(pk=int(lid))
	this_books = RelBookList.objects.filter(blist=this_lista).order_by('id')
	return render(request,'lista.html',{'this_lista':this_lista,'this_books':this_books})

def addprogressbar(request):
	this_book = Book.objects.get(pk=int(request.POST.get("book_id")))
	units = request.POST.get("units")
	cant = request.POST.get("cantidad")
	start_d = request.POST.get("start_date")

	newPB = ProgressBar.objects.create(libro = this_book,units=units,cantidad=cant,fecha_inicio = start_d)
	newPB.save()

	return redirect('/book/{}'.format(this_book.id))

def saveprogress(request):
	barra = ProgressBar.objects.get(pk=int(request.POST.get("barraid")))
	libro = Book.objects.get(pk=int(request.POST.get("bookid")))
	progreso = request.POST.get("progress")
	fecha = request.POST.get("fecha")

	delta = int(progreso) - barra.avance

	if (int(progreso) <= barra.cantidad	and int(progreso) > barra.avance):
		newLog = ProgressLog.objects.create(barra=barra,fecha=fecha,progreso=progreso, delta_lec=delta)
		newLog.save()
		ProgressBar.objects.filter(id=barra.id).update(avance=progreso)

	if (int(progreso)==barra.cantidad):
		newC = Consumo.objects.create(volume=libro,pages=barra.cantidad,start_d=barra.fecha_inicio, finish_d=fecha)
		newC.save()

	return redirect('/book/{}'.format(libro.id))

def statistics(request):

	paginas = ProgressLog.objects.raw("""
			select
			    1 as id,
			     strftime('%Y',date(fecha,'weekday 0')) as anho,
			      1*strftime('%m',date(fecha,'weekday 0'))-1 as mes,
			       1*strftime('%d',date(fecha,'weekday 0')) as dia,
			    sum(delta_lec) as paginas
			from
			    times_progresslog a
			    left join times_progressbar b
			    on a.barra_id=b.id
			    left join times_book c
			    on b.libro_id=c.id
			where
			    c.wtype_id in (9,10)
			group by
			      strftime('%Y',date(fecha,'weekday 0')) ,
			      1*strftime('%m',date(fecha,'weekday 0')) -1,
			       1*strftime('%d',date(fecha,'weekday 0'))

						    """)
	data_points = "["
	for p in paginas:
		data_points=data_points+"{ x: new Date("+ str(p.anho) +","+ str(p.mes) +" , "+ str(p.dia) +"), y: "+str(p.paginas)+" },"
	data_points=data_points+"]"

	capitulos = ProgressLog.objects.raw("""
			select
			    1 as id,
			     strftime('%Y',date(fecha,'weekday 0')) as anho,
			      1*strftime('%m',date(fecha,'weekday 0'))-1 as mes,
			       1*strftime('%d',date(fecha,'weekday 0')) as dia,
			    sum(delta_lec) as paginas ,
			    date(fecha,'weekday 0') fecha
			from
			    times_progresslog a
			    left join times_progressbar b
			    on a.barra_id=b.id
			    left join times_book c
			    on b.libro_id=c.id
			where
			    c.wtype_id in (11,12)
			group by
			      strftime('%Y',date(fecha,'weekday 0')) ,
			      1*strftime('%m',date(fecha,'weekday 0')) -1,
			       1*strftime('%d',date(fecha,'weekday 0')),
			       date(fecha,'weekday 0') order by date(fecha,'weekday 0') desc
						    """)
	data_points2 = "["
	for p in capitulos:
		data_points2=data_points2+"{ x: new Date("+ str(p.anho) +","+ str(p.mes) +" , "+ str(p.dia) +"), y: "+str(p.paginas)+" },"
	data_points2=data_points2+"]"

	return render(request, 'stats.html', { "data_points" : data_points, "data_points2":data_points2, 'capitulos':capitulos })


def saveshowprogress(request):
	barra = SeasonProgressBar.objects.get(pk=int(request.POST.get("barraid")))
	show = Show.objects.get(pk=int(request.POST.get("showid")))
	progreso = request.POST.get("progress")
	fecha = request.POST.get("fecha")

	delta = int(progreso) - barra.avance

	if (int(progreso) <= barra.temporada.episodes and int(progreso) > barra.avance):
		newLog = SeasonProgressLog.objects.create(barra=barra,fecha=fecha,progreso=progreso, delta_lec=delta)
		newLog.save()
		SeasonProgressBar.objects.filter(id=barra.id).update(avance=progreso)

	if (int(progreso)== barra.temporada.episodes):
		newC = ShowWatch.objects.create(sseason=barra.temporada,start_d=barra.fecha_inicio, finish_d=fecha)
		newC.save()

	return redirect('/show/{}'.format(show.id))

def addbookmedia(request):
	bid = request.POST.get("media_id")
	this_book = Book.objects.get(pk=int(bid))
	ix = request.FILES.get("imagen")
	img_type = int(request.POST.get("img_type"))

	newM = BookMedia.objects.create(libro=this_book,imgtype=img_type,imagen=ix)
	newM.save()

	return redirect('/book/{}'.format(this_book.id))


def addfilmmedia(request):
	bid = request.POST.get("media_id")
	this_movie = Movie.objects.get(pk=int(bid))
	ix = request.FILES.get("imagen")
	img_type = int(request.POST.get("img_type"))

	newM = MovieMedia.objects.create(film=this_movie,imgtype=img_type,imagen=ix)
	newM.save()

	return redirect('/movie/{}'.format(this_movie.id))
