#!/usr/bin/env python
#-*- coding:utf-8 -*-

import tornado.web,tornado.httpserver,tornado.escape,tornado.ioloop
import pymongo,os,hashlib,gravatar

class Application(tornado.web.Application):
    def __init__(self):
        adresler = [
                    (r"/",anasayfa),
                    
                    (r"/il/([a-zA-Z0-9%]+)",il),
                    (r"/il/([a-zA-Z0-9%]+)/",il),
                    
                    (r"/kullanici/([a-z0-9A-Z_.]+)",kullanici),
                    (r"/kullanici/([a-z0-9A-Z_.]+)/",kullanici),
                    
                    (r"/kayitol",kayitol),
                    (r"/kayitol/",kayitol),
                    
                    (r"/girisyap",girisyap),
                    (r"/girisyap/",girisyap),
                    
                    (r"/cikisyap",cikisyap),
                    (r"/cikisyap/",cikisyap),
                    
                    (r"/arama",arama),
                    (r"/arama/",arama),
                    
                    (r"/profil/duzenle",profil_duzenle),
                    (r"/profil/duzenle/",profil_duzenle),
                   ]

        ayarlar = dict(
                       template_path = os.path.join(os.path.dirname(__file__),"templates"),
                       static_path = os.path.join(os.path.dirname(__file__),"static"),
                       cookie_secret = "M=MT(?)^(5m097m/!')/B?)!(N(MIAUKJHNR(^!j3m075u3jpt4",
                       xsrf_cookies=True
                      )
        
        tornado.web.Application.__init__(self,adresler,**ayarlar)
        

class Base(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("kullanici_id")
    @property
    def db(self):
        return pymongo.Connection().harita
        
    def get_user_id(self,k_adi):
        if self.db.kullanici.find_one({"kullanici_adi":k_adi},{"_id":True}):
            self._id = self.db.kullanici.find_one({"kullanici_adi":k_adi},{"_id":True})["_id"]
            return str(self._id)
        else:
            return False
    
    def get_user_name(self):
        if self.current_user:
            return self.get_secure_cookie("kullanici_adi")
        else:
            return False
    
    
    
    
class anasayfa(Base):
    def get(self):
        import mapreduce
        il_ve_sayi = mapreduce.mapreduce()
        cc = self.db.kullanici.find()
        if self.current_user:
            self.render("index.html",kullanici_adi=self.get_user_name(),kullanicilar=cc,ilsayi = il_ve_sayi)
        else:
            self.render("index.html",kullanici_adi="",kullanicilar=cc,ilsayi = il_ve_sayi)
    
        
   

class kayitol(Base):
    def get(self):
        if not self.current_user:
            self.render("kayitol.html",kullanici_adi="")
        else:
            self.redirect("/")
    def post(self):
        kullanici_adi = self.get_argument("kullanici_adi")
        sifre = self.get_argument("sifre")
        sifre_tekrar = self.get_argument("sifre_tekrar")
        email = self.get_argument("email")
        ad = self.get_argument("ad")
        soyad = self.get_argument("soyad")
        il = self.db.iller.find_one({"plaka":self.get_argument("il")})["il"]
        lat = float(self.get_argument("lat"))
        lng = float(self.get_argument("lng"))
        kategori = self.get_argument("kategori")
        dagitim = self.get_argument("dagitim")
        
        if kullanici_adi!="" and sifre!="" and sifre_tekrar!="" and email!="" and ad!="" and soyad!="" and il!="" and lat!="" and lng!="" and kategori!="" and dagitim!="":
            if not self.db.kullanici.find_one({"kullanici_adi":kullanici_adi}):
                if sifre == sifre_tekrar:
                    avatar = gravatar.Gravatar(email,"",50).gravatar_url
                    yeni_kullanici = {"kullanici_adi":kullanici_adi,"sifre":hashlib.md5(sifre).hexdigest(),"email":email,"ad":ad,"soyad":soyad,"il":il,"koordinatlar":[float(lat),float(lng)],"kategori":kategori,"avatar":avatar,"dagitim":dagitim}
                    self.db.kullanici.save(yeni_kullanici)
                    self.set_secure_cookie("kullanici_id",self.get_user_id(kullanici_adi))
                    self.set_secure_cookie("kullanici_adi",kullanici_adi)
                    self.redirect("/kullanici/%s/" % kullanici_adi)
            else:
                self.write("Kullanıcı Zaten Kayıtlı.")
                # BURAYA BİR HTML DOSYASI ATABİLİRİZ VEYA İLERDE KAYIT İŞLEMİNİ AJAX KULLANARAK YAPABİLİRİM.   
        else:
            self.write("Doldurulması gereken alanlardan birini boş bıraktığınız için kayıt işleminiz tamamlanamamıştır.")
            
            
class girisyap(Base):
    def get(self):
        if not self.current_user:
            self.render("girisyap.html",kullanici_adi="")
        else:
            self.redirect("/")
    def post(self):
        if not self.current_user:
            kullanici_adi = self.get_argument("kullanici_adi",False)
            sifre = self.get_argument("sifre",False)
            if kullanici_adi and sifre:
                if self.db.kullanici.find_one({"kullanici_adi":kullanici_adi,"sifre":hashlib.md5(sifre).hexdigest()}):
                    self.set_secure_cookie("kullanici_id",self.get_user_id(kullanici_adi))
                    self.set_secure_cookie("kullanici_adi",kullanici_adi)
                    self.redirect("/kullanici/%s/" % kullanici_adi)
                else:
                    self.redirect("/girisyap/")
            else:
                self.redirect("/girisyap/")
        else:
            self.redirect("/")


class cikisyap(Base):
    def get(self):
        if not self.current_user:
            self.redirect("/")
        else:
            self.clear_cookie("kullanici_id")
            self.clear_cookie("kullanici_adi")
            self.redirect("/")





class il(Base):
    def get(self,i):
        if i.isdigit():
            il=self.db.iller.find_one({"plaka":i})["il"]
        else:
            il=i
        kullanicilar = self.db.kullanici.find({"il":il})
        v = self.db.kullanici.find({"il":il})
        self.render("illerdeki_kullanicilar.html",kullanici_adi=self.get_user_name(),kullanicilar=kullanicilar,k=v)

class kullanici(Base):
    def get(self,i):
        kullanici=self.db.kullanici.find_one({"kullanici_adi":i})
        yakinlardakiler = self.db.kullanici.find({"koordinatlar": {"$within": {"$center": [[float(kullanici["koordinatlar"][0]),float(kullanici["koordinatlar"][1])], 3]}}})
        if self.current_user:
            self.render("kullanici_profili.html",kullanici_adi=self.get_user_name(),kullanici = kullanici,avatar = gravatar.Gravatar(kullanici["email"],"",50).gravatar_url,yakinlardakiler=yakinlardakiler)
        else:
            self.render("kullanici_profili.html",kullanici_adi="",kullanici = kullanici,yakinlardakiler=yakinlardakiler)


class arama(Base):
    def get(self):
        if self.current_user:
            self.render("arama.html",kullanici_adi=self.get_user_name())
        else:
            self.render("arama.html",kullanici_adi="")
    def post(self):
        if self.current_user:
            if not self.get_argument("kategori") or self.get_argument("kategori") == "1":
                if self.get_argument("aranan","") != "":
                    bulunan = self.db.kullanici.find({"kullanici_adi":{"$regex":self.get_argument("aranan")}})
                else:
                    bulunan = self.db.kullanici.find()    
            else:
                if self.get_argument("aranan","") != "":
                    bulunan = self.db.kullanici.find({"kullanici_adi":{"$regex":self.get_argument("aranan")},"kategori":self.get_argument("kategori")})
                else:
                    bulunan = self.db.kullanici.find({"kategori":self.get_argument("kategori")})
            self.render("arama_sonuclari.html",kullanici_adi=self.get_user_name(),bulunan=bulunan)
        else:
           if not self.get_argument("kategori") or self.get_argument("kategori") == "1":
                if self.get_argument("aranan","") != "":
                    bulunan = self.db.kullanici.find({"kullanici_adi":{"$regex":self.get_argument("aranan")}})
                else:
                    bulunan = self.db.kullanici.find()    
           else:
                if self.get_argument("aranan","") != "":
                    bulunan = self.db.kullanici.find({"kullanici_adi":{"$regex":self.get_argument("aranan")},"kategori":self.get_argument("kategori")})
                else:
                    bulunan = self.db.kullanici.find({"kategori":self.get_argument("kategori")})
           self.render("arama_sonuclari.html",kullanici_adi="",bulunan=bulunan)
            
            


class profil_duzenle(Base):
    def get(self):
        if not self.current_user:
            self.redirect("/girisyap")
        else:
            bilgiler = self.db.kullanici.find({"kullanici_adi":self.get_user_name()})
            if self.db.iller.find_one({"il":bilgiler[0]["il"]}):
                _il = self.db.iller.find_one({"il":bilgiler[0]["il"]})["plaka"] or bilgiler[0]["il"]
            else:
                _il = bilgiler[0]["il"]
            self.render("profil_duzenle.html",kullanici_adi=self.get_user_name(),kullanici_bilgileri = bilgiler,il=_il,kb=bilgiler)
    def post(self):
        if not self.current_user:
            self.redirect("/girisyap")
        else:
            sifre = self.get_argument("sifre")
            sifre_tekrar = self.get_argument("sifre_tekrar")
            email = self.get_argument("email")
            ad = self.get_argument("ad")
            soyad = self.get_argument("soyad")
            il = self.db.iller.find_one({"plaka":str(self.get_argument("il"))})["il"]
            lat = self.get_argument("lat")
            lng = self.get_argument("lng")
            kategori = self.get_argument("kategori")
            dagitim = self.get_argument("dagitim")
            avatar = gravatar.Gravatar(email,"",50).gravatar_url
            print avatar
            if sifre!="" and sifre_tekrar!="" and sifre==sifre_tekrar and email!="" and ad!="" and soyad!="" and il!="" and lat!="" and lng!="" and kategori!="" and dagitim!="":
                self.db.kullanici.update({"kullanici_adi":self.get_user_name()},{"$set":{"kullanici_adi":self.get_user_name(),"sifre":hashlib.md5(sifre).hexdigest(),"email":email,"ad":ad,"soyad":soyad,"il":il,"koordinatlar":[float(lat),float(lng)],"kategori":kategori,"dagitim":dagitim,"avatar":avatar}})
                self.redirect("/kullanici/%s" % self.get_user_name())


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()


