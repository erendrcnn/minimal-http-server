# Eren D.

from datetime import datetime, timezone
import socket
import sys
import os

def temizle(filename):
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Eski kayit dosyasi \"{filename}\" silindi.")
    except OSError as e:
        print(f"Hata: {filename} dosyasi silinemedi. Hata Kodu: {e.strerror}")
    
def http_sunucu(host='localhost', port=8080, taramayi_engelle=False):
    sunucu_soketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # IPv4 ve TCP protokolu ile soket olusturulur.
    sunucu_soketi.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # Adresin tekrar kullanilmasi saglanir.
    
    # Gecici dosya belirlenir ve onceden kalan varsa silinir.
    filename = 'sunucu_veri.txt'
    temizle(filename)

    try:
        sunucu_soketi.bind((host, port))    # Sunucu soketi adresi ve portu ile baglar.
    except OSError as hata:
        if hata.errno == 98:                # Adres zaten kullanimda durumu
            print(f"{host}:{port} adresi zaten kullanimda. Sunucu baslatilamiyor.")
            sunucu_soketi.close()           # Sunucu soketini kapat.
            sys.exit(1)                     # Programi "1" hata kodu ile sonlandir.

    sunucu_soketi.listen(1)                 # Sunucu soketi dinlemeye baslar.
    print(f"{host}:{port} adresinde dinleniyor")

    try:
        while True:
            baglanti, adres = sunucu_soketi.accept()    # Baglanti kabul edilir.
            try:
                veri = b''
                while True:
                    parca = baglanti.recv(1024)    # 1024 byte'lik veri alinir.
                    if not parca:
                        break
                    veri += parca
                    if b'\r\n\r\n' in veri:
                        basliklar, govde = veri.split(b'\r\n\r\n', 1)
                        break

                istek = veri.decode('utf-8')            # Gelen veri utf-8 formatina cevrilir. (TR destekli)
                satirlar = istek.splitlines()           # Satirlara ayrilir.
                yanit = 'HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nGecersiz istek formati.\r\n'
                if satirlar:
                    ilk_satir = satirlar[0]
                    parcalar = ilk_satir.split()
                    if len(parcalar) < 3:                           # Gerekli parcalar gelmediyse.
                        yanit = 'HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nGecersiz istek formati.\r\n'
                    else:
                        metod, _, protokol = satirlar[0].split()    # Metod, yol ve protokol ayristirilir.
                        if protokol != 'HTTP/1.1':
                            yanit = 'HTTP/1.1 505 HTTP Version Not Supported\r\nConnection: close\r\n\r\nDesteklenmeyen HTTP surumu.\r\n'
                        else:
                            if metod == 'POST':
                                print(f"{adres} tarafindan POST baglantisi yapildi.")
                                if taramayi_engelle and any('User-Agent: curl' in satir for satir in satirlar): # curl taramasi engellenir.
                                    yanit = 'HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\nYetkisiz Erisim.\r\n'
                                else:
                                    for satir in basliklar.split(b'\r\n'):
                                        if b'Content-Length:' in satir:
                                            content_length = int(satir.split(b' ')[1])
                                            break
                                    if content_length:
                                        while len(govde) < content_length:
                                            govde += baglanti.recv(1024)
                                    govde = govde.decode('utf-8')
                                    with open(filename, 'a', encoding='utf-8') as dosya:
                                        dosya.write(govde + '\n')           # POST verisi dosyaya yazilir.
                                    yanit = (
                                        'HTTP/1.1 200 OK\r\n'
                                        f'Date: {datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}\r\n'
                                        'Content-Type: text/plain; charset=utf-8\r\n'
                                        'Connection: close\r\n'
                                        '\r\n'
                                        'POST alindi.\r\n'
                                    )
                                baglanti.sendall(yanit.encode('utf-8'))     # Yanit gonderilir.
                            elif metod == 'GET':
                                print(f"{adres} tarafindan GET baglantisi yapildi.")
                                if taramayi_engelle and any('User-Agent: curl' in satir for satir in satirlar): # curl taramasi engellenir.
                                    yanit = 'HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\nYetkisiz Erisim.\r\n'
                                else:
                                    try:
                                        with open(filename, 'r', encoding='utf-8') as dosya:
                                            dosya_icerigi = dosya.read()
                                            dosya_stat = os.stat(filename)
                                            etag = f'{dosya_stat.st_size}-{int(dosya_stat.st_mtime)}'
                                        yanit = (
                                            'HTTP/1.1 200 OK\r\n'
                                            f'Date: {datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}\r\n'
                                            'Content-Type: text/plain; charset=utf-8\r\n'
                                            f'Content-Length: {len(dosya_icerigi.encode("utf-8"))}\r\n'
                                            'Connection: close\r\n'
                                            'Server: CustomPythonServer/1.0\r\n'
                                            'Cache-Control: no-store\r\n'
                                            f'ETag: "{etag}"\r\n'
                                            f'Last-Modified: {datetime.fromtimestamp(dosya_stat.st_mtime, timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}\r\n'
                                            'Vary: Accept-Encoding\r\n'
                                            '\r\n'
                                            f'{dosya_icerigi}'
                                        )
                                    except FileNotFoundError:
                                        yanit = (
                                            'HTTP/1.1 404 Not Found\r\n'
                                            'Connection: close\r\n'
                                            'Content-Type: text/plain; charset=utf-8\r\n'
                                            '\r\n'
                                            'Veri bulunamadi.\r\n'
                                        )
                                    baglanti.sendall(yanit.encode('utf-8'))  # Her durumda yanit gonderilir.
                            else:
                                yanit = 'HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nDesteklenmeyen metod.\r\n'
                                baglanti.sendall(yanit.encode('utf-8'))     # Yanit gonderilir.
            finally:
                baglanti.close()                                            # Baglanti kapatilir.
    finally:
        sunucu_soketi.close()                                               # Sunucu soketi kapatilir.
        temizle(filename)                                                   # Program sonlandirilirken dosya silinir.

if __name__ == '__main__':
    taramayi_engelle = '--prevent-scraping' in sys.argv                     # "curl" engelleme icin gerekli arguman.
    http_sunucu(taramayi_engelle=taramayi_engelle)
