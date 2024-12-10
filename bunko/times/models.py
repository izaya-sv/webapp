from django.db import models
from datetime import datetime
from django.db import models
from django.utils import timezone
import os
from uuid import uuid4
from django.db.models import Q, Avg, Count, Min, Sum
from random import choice


def path_and_name(instance, filename):
    upload_to = 'wiki_media'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

class WikiType(models.Model):
	category = models.CharField(max_length=255)

	def __str__(self):
		return self.category

class Wiki(models.Model):
	wtype = models.ForeignKey(WikiType,on_delete=models.CASCADE)
	title = models.CharField(max_length=512)
	info = models.TextField()
	created_at = models.DateTimeField(auto_now=True)
	updated_at = models.DateTimeField(null=True,blank=True)

	def __str__(self):
		return self.title

	@property
	def headtext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info[0:350]
		else:
			return self.info[0:n_corte]

	@property
	def cleantext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info
		else:
			return self.info.replace('==headtext==','')

	@property
	def fecha_c(self):
		return self.updated_at.strftime("%Y-%m-%d")


class Book(models.Model):
	title = models.CharField(max_length=512)
	orig_lan = models.CharField(max_length=2)
	info = models.TextField()
	pub_year = models.IntegerField()
	wtype = models.ForeignKey(WikiType,on_delete=models.CASCADE)

	def __str__(self):
		return self.title+' ('+ str(self.pub_year) +')'

	@property
	def headtext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info[0:350]
		else:
			return self.info[0:n_corte]

	@property
	def cleantext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info
		else:
			return self.info.replace('==headtext==','')

	@property
	def titulo(self):
		return self.title+' ('+ str(self.pub_year) +')'

	@property
	def authors_links(self):
		creds = Credito.objects.filter(ctype__id__in=[1,5,6,7],media_type=1,media_id=self.id)

		enlaces = ""

		for c in creds:
			enlaces = enlaces + "<a href='/wiki/"+str(c.persona.id)+"' style='text-decoration:none; color:#6F8FAF;'>"+c.persona.title+"</a>,&nbsp;"

		return enlaces[:-7]

	@property
	def rhist(self):
		conteo = Consumo.objects.filter(volume__id=self.id).count()
		if conteo == 0:
			rcheck = 0
		else:
			rcheck = 1
		return rcheck

	@property
	def last_read(self):
		conteo = Consumo.objects.filter(volume__id=self.id).count()
		if conteo == 0:
			rcheck = None
		else:
		    robject = Consumo.objects.filter(volume__id=self.id).latest('-finish_d')
		    rcheck = robject.finish_d
		return rcheck

	@property
	def mainPic(self):
		npics = BookMedia.objects.filter(libro__id=self.id,imgtype=1).count()
		if npics == 0:
			return None
		else:
			pks = BookMedia.objects.filter(libro__id=self.id,imgtype=1).values_list('pk', flat=True)
			random_pk = choice(pks)
			ppic = BookMedia.objects.get(pk=random_pk)
			return ppic.imagen.url


class CreditType(models.Model):
	credit_type = models.CharField(max_length=255)
	def __str__(self):
		return self.credit_type

class Credito(models.Model):
	ctype = models.ForeignKey(CreditType,on_delete=models.CASCADE)
	persona = models.ForeignKey(Wiki,on_delete=models.CASCADE)
	media_type = models.IntegerField()
	media_id = models.IntegerField()

	def __str__(self):
		return self.persona.title

class Movie(models.Model):
	title = models.CharField(max_length=512)
	info = models.TextField()
	premiere = models.IntegerField()
	runtime = models.IntegerField()

	def __str__(self):
		return self.title+' ('+ str(self.premiere) +')'

	@property
	def titulo(self):
		return self.title+' ('+ str(self.premiere) +')'
	@property
	def headtext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info[0:350]
		else:
			return self.info[0:n_corte]

	@property
	def cleantext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info
		else:
			return self.info.replace('==headtext==','')

	@property
	def mainPic(self):
		npics = MovieMedia.objects.filter(film__id=self.id,imgtype=1).count()
		if npics == 0:
			return None
		else:
			pks = MovieMedia.objects.filter(film__id=self.id,imgtype=1).values_list('pk', flat=True)
			random_pk = choice(pks)
			ppic = MovieMedia.objects.get(pk=random_pk)
			return ppic.imagen.url


class Show(models.Model):
	title = models.CharField(max_length=512)
	info = models.TextField()
	wtype = models.ForeignKey(WikiType,on_delete=models.CASCADE)
	def __str__(self):
		return self.title

	@property
	def headtext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info[0:350]
		else:
			return self.info[0:n_corte]

	@property
	def cleantext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info
		else:
			return self.info.replace('==headtext==','')
	@property
	def consumos(self):
		ncons = ShowWatch.objects.filter(sseason__show__id=self.id).count()

		return ncons

	@property
	def transmision(self):
		premiers = Season.objects.filter(show=self).values_list('premiere',flat=True)

		max_p = max(premiers)
		min_p = min(premiers)

		if max_p == min_p:
			str_t = str(max_p)
		else:
			str_t = str(min_p)+'-'+str(max_p)

		return str_t

	@property
	def conteo_s(self):
		n_seasons = Season.objects.filter(show__id = self.id).count()

		return n_seasons


class Season(models.Model):
	show = models.ForeignKey(Show,on_delete=models.CASCADE)
	season_t = models.CharField(max_length=255, null=True, blank=True)
	info = models.TextField()
	episodes = models.IntegerField()
	avg_runtime = models.IntegerField()
	premiere = models.IntegerField()

	def __str__(self):
		return self.show.title+' '+self.season_t+' ('+ str(self.premiere) +')'

	@property
	def titulo(self):
		if len(self.season_t)<=3:
			return self.show.title+' '+self.season_t+' ('+ str(self.premiere) +')'
		else:
			return self.season_t+' ('+ str(self.premiere) +')'
	@property
	def headtext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info[0:350]
		else:
			return self.info[0:n_corte]

	@property
	def cleantext(self):
		n_corte = self.info.find('==headtext==')
		if n_corte == -1:
			return self.info
		else:
			return self.info.replace('==headtext==','')

	@property
	def consumos(self):
		n_cons = ShowWatch.objects.filter(sseason__id = self.id).count()

		return n_cons

	@property
	def barras(self):
		n_barras = SeasonProgressBar.objects.filter(temporada=self, avance__lt=self.episodes).count()

		return n_barras

	@property
	def actual_barras(self):
		n_barras = SeasonProgressBar.objects.filter(temporada=self, avance__lt=self.episodes).count()

		if n_barras > 0:
			this_barras = SeasonProgressBar.objects.filter(temporada=self, avance__lt=self.episodes)
			return this_barras
		else:
			return None

class Consumo(models.Model):
	volume = models.ForeignKey(Book,on_delete=models.CASCADE)
	pages = models.IntegerField()
	start_d = models.DateField()
	finish_d = models.DateField()



	def __str__(self):
		return self.volume.titulo

class Pagina(models.Model):
	titulo = models.CharField(max_length=255)
	info = models.TextField()
	def __str__(self):
		return self.titulo

class PageRels(models.Model):
	page = models.ForeignKey(Pagina, on_delete=models.CASCADE)
	child = models.ForeignKey(Wiki,on_delete=models.CASCADE)

	def __str__(self):
		return self.page.titulo

class MovieWatch(models.Model):
	film = models.ForeignKey(Movie, on_delete=models.CASCADE)
	wdate = models.DateField()

	def __str__(self):
		return self.film.titulo

class ShowWatch(models.Model):
	sseason = models.ForeignKey(Season,on_delete=models.CASCADE)
	start_d = models.DateField()
	finish_d = models.DateField()

	def __str__(self):
		return self.sseason.show.title+' '+self.sseason.season_t

class MediaWiki(models.Model):
	mwiki = models.ForeignKey(Wiki, on_delete=models.CASCADE)
	media_type = models.IntegerField()
	media_id = models.IntegerField()

	def __str__(self):
		return self.mwiki.title

class BookList(models.Model):
	listname = models.CharField(max_length=500)
	date_created = models.DateField(auto_now=True)
	listinfo = models.TextField()

	def __str__(self):
		return self.listname

	@property
	def conteo(self):
		cont = RelBookList.objects.filter(blist=self).count()

		return cont

	@property
	def lecturas(self):
		n_lecturas = RelBookList.objects.filter(blist=self, bbook__consumo__finish_d__gt=self.date_created).count()
		return n_lecturas


class RelBookList(models.Model):
	blist = models.ForeignKey(BookList,on_delete=models.CASCADE)
	bbook =models.ForeignKey(Book,on_delete=models.CASCADE)

	def __str__(self):
		return self.blist.listname+' - '+self.bbook.titulo

class ProgressBar(models.Model):
	libro = models.ForeignKey(Book,on_delete=models.CASCADE)
	units = models.CharField(max_length=50)
	cantidad = models.IntegerField()
	avance = models.IntegerField(blank=True,default=0)
	fecha_inicio = models.DateField()


	def __str__(self):
		return self.libro.titulo

	@property
	def prct_prog(self):
		return round(self.avance/self.cantidad*100.00,2)


class ProgressLog(models.Model):
	barra = models.ForeignKey(ProgressBar,on_delete=models.CASCADE)
	fecha = models.DateField()
	progreso = models.IntegerField()
	delta_lec = models.IntegerField(default=0)

	def __str__(self):
		return str(self.id)+'-'+self.barra.libro.titulo


class SeasonProgressBar(models.Model):
	temporada = models.ForeignKey(Season, on_delete=models.CASCADE)
	avance = models.IntegerField(blank=True,default=0)
	fecha_inicio = models.DateField()

	def __str__(self):
		return self.temporada.titulo

	@property
	def prct_prog(self):
		return round(self.avance/self.temporada.episodes*100.00,2)

class SeasonProgressLog(models.Model):
	barra = models.ForeignKey(SeasonProgressBar,on_delete=models.CASCADE)
	fecha = models.DateField()
	progreso = models.IntegerField()
	delta_lec = models.IntegerField(default=0)

	def __str__(self):
		return str(self.id)+'-'+self.barra.temporada.titulo

class BookMedia(models.Model):
	libro = models.ForeignKey(Book,on_delete=models.CASCADE)
	imgtype = models.IntegerField()
	imagen = models.ImageField(upload_to=path_and_name, max_length=255, null=True, blank=True)

	def __str__(self):
		return self.libro.titulo

class MovieMedia(models.Model):
	film = models.ForeignKey(Movie,on_delete=models.CASCADE)
	imgtype = models.IntegerField()
	imagen = models.ImageField(upload_to=path_and_name, max_length=255, null=True, blank=True)

	def __str__(self):
		return self.film.titulo

class ItemMedia(models.Model):
	item = models.ForeignKey(Wiki,on_delete=models.CASCADE)
	imgtype = models.IntegerField()
	imagen = models.ImageField(upload_to=path_and_name, max_length=255, null=True, blank=True)

	def __str__(self):
		return self.item.title

class MovieCredit(models.Model):
	film = models.ForeignKey(Movie,on_delete=models.CASCADE)
	credit = models.CharField(max_length=200)
	persona = models.CharField(max_length=200)
	def __str__(self):
		return self.persona+' @ '+ self.film.titulo

class BookDuel(models.Model):
	left_b = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='left_b')
	right_b = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='right_b')
	win_b = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='win_b')

	def __str__(self):
		return self.left_b.titulo+' @ '+ self.right_b.titulo


class MovieDuel(models.Model):
	left_b = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='left_b')
	right_b = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='right_b')
	win_b = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='win_b')

	def __str__(self):
		return self.left_b.titulo+' @ '+ self.right_b.titulo


class TimesMedia(models.Model):
	title = models.CharField(max_length=512)
	imgtype = models.IntegerField()
	imagen = models.ImageField(upload_to=path_and_name, max_length=255, null=True, blank=True)

	def __str__(self):
		return self.title



























