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
import random


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
	wtypes = WikiType.objects.filter(category__in=['blog','character','event','journal','news','review']).order_by('category')

	if request.method == 'POST':
		this_cat = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
		this_titulo = request.POST.get("title")
		this_info = request.POST.get("info")

		newW = Wiki.objects.create(wtype=this_cat,title=this_titulo,info=this_info,updated_at=datetime.now())
		newW.save()

		return redirect('/wiki/{}'.format(newW.id))
	else:
		return render(request,'add-wiki.html',{'wtypes':wtypes})

def addpersona(request):
	wtypes = WikiType.objects.all().order_by('category')

	if request.method == 'POST':
		this_cat = WikiType.objects.get(pk=int(request.POST.get("cat_id")))
		this_titulo = request.POST.get("title")
		this_info = request.POST.get("info")

		newW = Wiki.objects.create(wtype=this_cat,title=this_titulo,info=this_info,updated_at=datetime.now())
		newW.save()

		return redirect('/wiki/{}'.format(newW.id))
	else:
		return render(request,'add-persona.html',{'wtypes':wtypes})

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
	articles = Wiki.objects.all().exclude(wtype__id__in=[1,2,3,4,5,8]).exclude(id=42).order_by('-updated_at')[0:nlist]
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

		
		
		if len(request.POST.get("tags",""))>0:
			tags = request.POST.get("tags","").split(",")
			for t in tags:
				bt = BookTag.objects.create(libro=newB,tag=t)
				bt.save()

		return redirect('/book/{}'.format(newB.id))
	else:
		return render(request,'add-book.html',{'personas':personas,'booktypes':booktypes})

def book(request,bookid):
	this_book = Book.objects.get(pk=int(bookid))
	wtypes = WikiType.objects.all()
	related_wikis = MediaWiki.objects.filter(media_type=1, media_id=this_book.id).order_by('-id')
	listas = BookList.objects.all().order_by('listname')

	barras = ProgressBar.objects.filter(libro=this_book,avance__lt=F('cantidad'))

	btags = BookTag.objects.filter(libro__id=this_book.id)

	return render(request,'view-book.html',{'this_book':this_book,'btags':btags,'wtypes':wtypes,'relw':related_wikis,'blistas':listas,'barras':barras})

def books(request,y):
	max_year = Consumo.objects.order_by('-finish_d').first()

	if int(y)==1:
		y = max_year.finish_d.strftime('%Y')

	conteo = Consumo.objects.filter(volume__wtype__id=9).count()
	anhos = Consumo.objects.filter(volume__wtype__id=9).values('finish_d__year').annotate(qbooks=Count('id')).order_by('-finish_d__year')
	rqueue = Book.objects.filter(consumo__volume__isnull=True, wtype__id=9).order_by('pub_year')
	rhist = Consumo.objects.filter(volume__wtype__id=9,finish_d__year=int(y)).order_by('-finish_d','-id')

	return render(request,'view-history.html',{'rhist':rhist,'rqueue':rqueue,'anhos':anhos,'anho':y,'conteo':conteo})

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
	director = MovieCredit.objects.filter(film__id=this_movie.id, credit = 'Director' )
	cast = MovieCredit.objects.filter(film__id=this_movie.id, credit = 'Main Cast')

	return render(request,'view-movie.html',{'this_movie':this_movie,'wtypes':wtypes,'relw':related_wikis,'director':director,'cast':cast})

def watchmovie(request):
	wmovie = Movie.objects.get(pk=int(request.POST.get("movieid")))

	fecha_i = request.POST.get("start_d")

	newR = MovieWatch.objects.create(film=wmovie,wdate=fecha_i)
	newR.save()

	return redirect('/movie/{}'.format(wmovie.id))

def movies(request,y):

	max_year = MovieWatch.objects.order_by('-wdate').first()

	if int(y)==1:
		y = max_year.wdate.strftime('%Y')

	conteo = MovieWatch.objects.count()
	anhos = MovieWatch.objects.values('wdate__year').annotate(qbooks=Count('id')).order_by('-wdate__year')

	wmovies = MovieWatch.objects.filter(wdate__year=int(y)).order_by('-wdate')
	return render(request,'movie-history.html',{'wmovies':wmovies,'anho':int(y),'conteo':conteo,'anhos':anhos})

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
	import datetime
	this_book = Book.objects.get(pk=int(request.POST.get("book_id")))
	units = request.POST.get("units")
	cant = request.POST.get("cantidad")
	start_d = request.POST.get("start_date")

	conteo = Consumo.objects.filter(volume=this_book,start_d=datetime.datetime(1999, 12, 31)).count()


	if conteo > 0:
		Consumo.objects.filter(volume=this_book,start_d=datetime.datetime(1999, 12, 31)).delete()

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

def savepost(request):
	fecha = request.POST.get("fecha")
	entry = request.POST.get("entrada")
	this_cat = WikiType.objects.get(pk=8)
	datetime_object = datetime.strptime(fecha+' 00:00:00', '%Y-%m-%d %H:%M:%S')

	conteo = Wiki.objects.filter(wtype__id=8,updated_at=datetime_object).count()

	if conteo == 0:
		newW = Wiki.objects.create(wtype=this_cat,title='Journal Entry',info='<p>'+entry,updated_at=datetime_object)
		newW.save()
	else:
		prev = Wiki.objects.filter(wtype__id=8,updated_at=datetime_object).latest('-id')

		Wiki.objects.filter(id=prev.id).update(info = prev.info+'<p>'+entry)


	return redirect('/journal/1')

def journal(request,y):
	max_year = Wiki.objects.filter(wtype__id=8).order_by('-updated_at').first()

	if int(y)==1:
		y = max_year.updated_at.strftime('%Y')

	anhos = Wiki.objects.filter(wtype__id=8).values('updated_at__year').annotate(qitems=Count('id')).order_by('-updated_at__year')
	posts = Wiki.objects.filter(wtype__id=8,updated_at__year=int(y)).order_by('-updated_at','id')
	return render(request,'journal.html',{'posts':posts,'anhos':anhos,'anho':int(y)})



def mediastats(request):

	paginas = SeasonProgressLog.objects.raw("""
			with todo as (select
			    1 as id,
			    'shows' type,
			    strftime('%Y',date(a.fecha,'weekday 0')) as anho,
			    1*strftime('%m',date(a.fecha,'weekday 0'))-1 as mes,
			    1*strftime('%d',date(a.fecha,'weekday 0')) as dia,
			    round(sum(a.delta_lec*c.avg_runtime/60.0),1) as horas ,
			    date(a.fecha,'weekday 0') fecha
			from
			    times_seasonprogresslog a
			    left join times_seasonprogressbar b
			    on a.barra_id = b.id
			    left join times_season c
			    on b.temporada_id = c.id
			where
			    a.fecha >= '2024-10-01'
			group by
			    strftime('%Y',date(a.fecha,'weekday 0')),
			    1*strftime('%m',date(a.fecha,'weekday 0'))-1,
			    1*strftime('%d',date(a.fecha,'weekday 0')),
			    date(a.fecha,'weekday 0')

			union all

			select
			    1 as id,
			    'movies' type,
			    strftime('%Y',date(a.wdate,'weekday 0')) as anho,
			    1*strftime('%m',date(a.wdate,'weekday 0'))-1 as mes,
			    1*strftime('%d',date(a.wdate,'weekday 0')) as dia,
			    round(sum(b.runtime/60.0),1) as horas ,
			    date(a.wdate,'weekday 0') fecha
			from
			    times_moviewatch a
			    left join times_movie b
			    on a.film_id = b.id
			where
			    a.wdate >= '2024-10-01'
			group by
			    strftime('%Y',date(a.wdate,'weekday 0')),
			    1*strftime('%m',date(a.wdate,'weekday 0'))-1,
			    1*strftime('%d',date(a.wdate,'weekday 0')),
			    date(a.wdate,'weekday 0') )

			select
				1 as id,
			    anho,
			    mes,
			    dia,
			    fecha,
			    sum(horas) as horas
			from
			    todo
			group by
			    anho,
			    mes,
			    dia,
			    fecha

									    """)
	data_points = "["
	for p in paginas:
		data_points=data_points+"{ x: new Date("+ str(p.anho) +","+ str(p.mes) +" , "+ str(p.dia) +"), y: "+str(p.horas)+" },"
	data_points=data_points+"]"


	return render(request, 'media-stats.html', { "data_points" : data_points })

def addmoviecredits(request):
	director = request.POST.get("director")
	cast = request.POST.get("cast")
	movie = Movie.objects.get(pk=int(request.POST.get("movie_id")))

	for strC in request.POST.get("director","").split(","):
		newMC = MovieCredit.objects.create(film=movie,credit='Director',persona=strC.strip())
		newMC.save()

	for strC in request.POST.get("cast","").split(","):
		newMC = MovieCredit.objects.create(film=movie,credit='Main Cast',persona=strC.strip())
		newMC.save()

	return redirect('/movie/{}'.format(movie.id))

def movieperson(request,strPersona):
	creditos = MovieCredit.objects.filter(persona=strPersona).order_by('-film__premiere')
	personas = MovieCredit.objects.values('persona').annotate(ncredits = Count('id')).order_by('-ncredits','persona')[0:30]
	this_persona = strPersona

	return render(request,'movie-person.html',{'creditos':creditos,'personas':personas,'this_persona':this_persona})

def bookduel(request):


	n_duelos  = BookDuel.objects.raw("""
	select
		1 as id,
	    count(1) as conteo
	 from
	    posibles_duelos a
	    left join times_bookduel b
	    on a.volume_izq = b.left_b_id and a.volume_der = b.right_b_id
	    left join times_bookduel c
	    on a.volume_izq = c.right_b_id and a.volume_der = c.left_b_id
	where
	    b.id is null and c.id is null""")

	for n in n_duelos:
		n_d = n.conteo

	if n_d > 0:
		elegido = random.randint(0, (n_d)-1)

		duelos = BookDuel.objects.raw("""
		select
		    a.id,
		    a.volume_der,
		    a.volume_izq
		from
		    posibles_duelos a
		    left join times_bookduel b
		    on a.volume_izq = b.left_b_id and a.volume_der = b.right_b_id
		    left join times_bookduel c
		    on a.volume_izq = c.right_b_id and a.volume_der = c.left_b_id
		where
		    b.id is null and c.id is null""")[elegido]



		random_obj = Book.objects.get(pk=duelos.volume_izq)
		random_obj2 = Book.objects.get(pk=duelos.volume_der)


		conteo_1 = BookDuel.objects.filter(left_b__id=int(random_obj.id),right_b__id=int(random_obj2.id)).count()
		conteo_2 = BookDuel.objects.filter(left_b__id=int(random_obj2.id),right_b__id=int(random_obj.id)).count()
		conteo_t = conteo_1 + conteo_2
	else:
		elegido = 0
		random_obj = None
		random_obj2 = None
		conteo_t = None

	topbooks = BookDuel.objects.raw("""
		select
		    1 as id,
		    conteos.*,
		    datos.title,
		    datos.pub_year,
		    case
		    	when conteos.duels <= 5 then 0
		    	when conteos.duels <= 10 then 1
		    	when conteos.duels <= 25 then 2
		    	else 3
		    end flag_votes,

		    round(100.000*conteos.wins/conteos.duels,1) as rank_p
		from
		    (select
		        book_id,
		        sum(c) as duels,
		        sum(wins) as wins
		    from
		        (select
		            left_b_id as book_id,
		            count(1) c,
		            sum(case when win_b_id=left_b_id then 1 else 0 end) wins
		        from
		            times_bookduel
		        group by
		            left_b_id

		        union all

		        select
		            right_b_id book_id,
		            count(1) c,
		            sum(case when win_b_id=right_b_id then 1 else 0 end) wins
		        from
		            times_bookduel
		        group by
		            right_b_id ) as x
		    group by
		        book_id) conteos
		    left join times_book datos
		    on conteos.book_id = datos.id
		order by
			case
		    	when conteos.duels <= 5 then 0
		    	when conteos.duels <= 10 then 1
		    	when conteos.duels <= 25 then 2
		    	else 3
		    end desc,
		    100.000*conteos.wins/conteos.duels desc,  conteos.duels desc """)

	return render(request,'book_duel.html',{'book1':random_obj,'book2':random_obj2,'topbooks':topbooks, 'conteo_t':conteo_t,'n_duelos':n_d})


def savebookduel(request,l,r,w):

	conteo_1 = BookDuel.objects.filter(left_b__id=int(l),right_b__id=int(r)).count()
	conteo_2 = BookDuel.objects.filter(left_b__id=int(r),right_b__id=int(l)).count()

	conteo_t = conteo_2 + conteo_1

	if conteo_t == 0:
		book1 = Book.objects.get(pk=int(l))
		book2 = Book.objects.get(pk=int(r))
		book3 = Book.objects.get(pk=int(w))
		newBD = BookDuel.objects.create(left_b=book1,right_b=book2,win_b=book3)

	return redirect('/bookduel')


def movieduel(request):

	n_duelos  = MovieDuel.objects.raw("""
	select
	    1 as id,
	    count(1) as conteo
	from
	    movie_duelosp a
	    left join times_movieduel b
	    on a.volume_izq = b.left_b_id and a.volume_der = b.right_b_id
	    left join times_movieduel c
	    on a.volume_izq = c.right_b_id and a.volume_der = c.left_b_id
	where
	    b.id is null and c.id is null""")

	for n in n_duelos:
		n_d = n.conteo


	if n_d > 0:
		elegido = random.randint(0, (n_d)-1)
		duelos = MovieDuel.objects.raw("""
		select
		    a.id,
		    a.volume_der,
		    a.volume_izq
		from
		    movie_duelosp a
		    left join times_movieduel b
		    on a.volume_izq = b.left_b_id and a.volume_der = b.right_b_id
		    left join times_movieduel c
		    on a.volume_izq = c.right_b_id and a.volume_der = c.left_b_id
		where
		    b.id is null and c.id is null""")[elegido]

		random_obj = Movie.objects.get(pk=duelos.volume_izq)
		random_obj2 = Movie.objects.get(pk=duelos.volume_der)
		conteo_1 = MovieDuel.objects.filter(left_b__id=int(random_obj.id),right_b__id=int(random_obj2.id)).count()
		conteo_2 = MovieDuel.objects.filter(left_b__id=int(random_obj2.id),right_b__id=int(random_obj.id)).count()
		conteo_t = conteo_1 + conteo_2
	else:
		elegido = 0
		random_obj = None
		random_obj2 = None
		conteo_t = None




	topbooks = MovieDuel.objects.raw("""
		select
		    1 as id,
		    conteos.*,
		    datos.title,
		    datos.premiere,
		    case
		    	when conteos.duels <= 5 then 0
		    	when conteos.duels <= 10 then 1
		    	when conteos.duels <= 25 then 2
		    	else 3
		    end flag_votes,
		    round(conteos.wins*100.00/conteos.duels,1) rank_p
		from
		    (select
		        book_id,
		        sum(c) as duels,
		        sum(wins) as wins
		    from
		        (select
		            left_b_id as book_id,
		            count(1) c,
		            sum(case when win_b_id=left_b_id then 1 else 0 end) wins
		        from
		            times_movieduel
		        group by
		            left_b_id

		        union all

		        select
		            right_b_id book_id,
		            count(1) c,
		            sum(case when win_b_id=right_b_id then 1 else 0 end) wins
		        from
		            times_movieduel
		        group by
		            right_b_id ) as x
		    group by
		        book_id) conteos
		    left join times_movie datos
		    on conteos.book_id = datos.id
		order by
			case
		    	when conteos.duels <= 5 then 0
		    	when conteos.duels <= 10 then 1
		    	when conteos.duels <= 25 then 2
		    	else 3
		    end desc,
		    conteos.wins*1.00/conteos.duels desc,  conteos.duels desc """)



	return render(request,'movie_duel.html',{'book1':random_obj,'book2':random_obj2,'topbooks':topbooks,'conteo_t':conteo_t})


def savemovieduel(request,l,r,w):

	conteo_1 = MovieDuel.objects.filter(left_b__id=int(l),right_b__id=int(r)).count()
	conteo_2 = MovieDuel.objects.filter(left_b__id=int(r),right_b__id=int(l)).count()

	conteo_t = conteo_2 + conteo_1

	if conteo_t == 0:
		book1 = Movie.objects.get(pk=int(l))
		book2 = Movie.objects.get(pk=int(r))
		book3 = Movie.objects.get(pk=int(w))
		newBD = MovieDuel.objects.create(left_b=book1,right_b=book2,win_b=book3)

	return redirect('/movieduel')

def quemarlibro(request,libro):

	libro = Book.objects.get(pk=int(libro))
	conteo_2 = Consumo.objects.create(volume = libro, pages=1,start_d='1999-12-31',finish_d='1999-12-31')
	conteo_2.save()



	return redirect('/book/{}'.format(libro.id))


def moviedbImport(request):
    import requests
    import json

    movie_id = request.POST.get("title")

    url = "https://api.themoviedb.org/3/movie/{}?language=en-US".format(movie_id)
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NmM4MjVlMDFiY2RiMWQ1NWQ4YjRmYzNiNDQ0ODFhZiIsInN1YiI6IjYwMWM1NmFkNzMxNGExMDAzZGZjMzhiOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.vnpzsejhhlKDqssAg1dHiMH64Ja4_bP2UPcJFgHrW3k"
    }

    response = requests.get(url, headers=headers)
    movie_dict = json.loads(response.text)
    movie_dict3 = json.loads(response.text)

    str_titulo = movie_dict['original_title']
    str_overview = movie_dict['overview']
    str_premiere = movie_dict['release_date']
    str_runtime= movie_dict['runtime']
    str_poster = "https://image.tmdb.org/t/p/w200{}".format(movie_dict['poster_path'])

    url = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US".format(movie_id)

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NmM4MjVlMDFiY2RiMWQ1NWQ4YjRmYzNiNDQ0ODFhZiIsInN1YiI6IjYwMWM1NmFkNzMxNGExMDAzZGZjMzhiOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.vnpzsejhhlKDqssAg1dHiMH64Ja4_bP2UPcJFgHrW3k"
    }

    response = requests.get(url, headers=headers)
    movie_dict = json.loads(response.text)

    int_c = 0
    str_director = ""
    for c in movie_dict['crew']:
        if c['job']=='Director':
            str_director = str_director+c['original_name']+","

    str_director = str_director[:-1]

    str_cast = ""
    for c in movie_dict['cast'][0:12]:
        str_cast = str_cast+c['original_name']+","

    str_cast = str_cast[:-1]

    str_tags = str_director+","+str_premiere[0:4]+","+str_cast

    return render(request,'add-moviedb.html',{'str_tags':str_tags,'str_titulo':str_titulo,'str_overview':str_overview,'str_premiere':str_premiere[0:4],'str_runtime':str_runtime,'str_poster':str_poster,'str_director':str_director,'str_cast':str_cast})

def savemovie(request):
	mtitle = request.POST.get("title")
	mpremiere = request.POST.get("premiere")
	mruntime = request.POST.get("runtime")
	minfo = request.POST.get("info")

	newM = Movie.objects.create(title=mtitle,premiere=mpremiere,runtime=mruntime,info=minfo)
	newM.save()

	director = request.POST.get("director")
	cast = request.POST.get("cast")
	movie = Movie.objects.get(pk=newM.id)

	for strC in request.POST.get("director","").split(","):
		newMC = MovieCredit.objects.create(film=movie,credit='Director',persona=strC.strip())
		newMC.save()

	for strC in request.POST.get("cast","").split(","):
		newMC = MovieCredit.objects.create(film=movie,credit='Main Cast',persona=strC.strip())
		newMC.save()



	return redirect('/movie/{}'.format(newM.id))

def addtimesmedia(request):
	if request.method == 'POST':
		info = request.POST.get("descripcion")
		ix = request.FILES.get("imagen")
		newM = TimesMedia.objects.create(title=info,imgtype=1,imagen=ix)
		newM.save()
		return redirect('/mediapage')
	else:
		return render(request,'add-times-media.html',{})

def mediapage(request,p):

	conteo = TimesMedia.objects.all().count()

	ppp = 10

	paginas = math.ceil(conteo/ppp)

	if (int(p)+1) == paginas:
		next_p = 0 
	else:
		next_p = (int(p)+1)



	medias = TimesMedia.objects.all().order_by('-id')[int(p)*ppp:(int(p)*ppp)+ppp]

	return render(request,'times-album.html',{'medias':medias,'next_p':next_p,'paginas':paginas,'next_p':next_p})

def addbooktags(request):
	this_libro = Book.objects.get(pk=int(request.POST.get("book")))
	tags = request.POST.get("tags","").split(",")

	for t in tags:
		bt = BookTag.objects.create(libro=this_libro,tag=t)
		bt.save()

	return redirect('/book/{}'.format(request.POST.get("book")))

def viewbooktag(request,this_tag):

	books = BookTag.objects.filter(tag=this_tag)

	now_tag = this_tag

	return render(request,'view-booktag.html',{'books':books,'now_tag':now_tag})