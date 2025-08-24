# Modulus
MODULUS, Discord sunucularınız için geliştirilmiş kapsamlı bir moderasyon ve eğlence botudur. 
Sunucularda düzeni korumanıza yardımcı olurken, kullanıcı etkileşimini artıracak birçok özellik sunar. 

🚀 Öne çıkan özellikler:
- 🔒 Gelişmiş Moderasyon (uyarı, mute, ban, clear, reklam/küfür/flood engeli)
- ⭐ XP & Level sistemi (otomatik rol dağıtımı ve duyurular)
- 📝 Öneri & Oylama sistemi
- 🎭 AFK sistemi
- 🎶 Rastgele şarkı önerileri
- 📜 Loglama (silinen/düzenlenen mesajlar, mod geçmişi)
- 🛡️ Autorol ve dil rolleri desteği
- 🤖 GPT-4 entegrasyonu ile akıllı sohbet

Bu bot, hem **topluluk güvenliğini sağlamak** hem de **eğlenceli bir deneyim sunmak** için tasarlanmıştır.

# Genel Komutlar
| Komut                    | Açıklama                                                      |
| ------------------------ | ------------------------------------------------------------- |
| `/ping`                  | Botun gecikmesini (ms cinsinden) gösterir.                    |
| `/avatar [kullanıcı]`    | Bir kullanıcının avatarını gösterir.                          |
| `/kullanici [kullanıcı]` | Kullanıcı hakkında bilgi verir (ID, hesap tarihi, level vb).  |
| `/sunucu`                | Sunucu hakkında genel bilgileri gösterir.                     |
| `/sarki`                 | Rastgele bir şarkı önerir.                                    |
| `/afk [mesaj]`           | AFK moduna geçer. Etiketlendiğinde AFK mesajınız gösterilir.  |
| `/sync`                  | Botun komutlarını Discord ile senkronize eder (sadece owner). |

# Moderasyon Komutları
| Komut                      | Açıklama                                                     | Gereken Yetki    |
| -------------------------- | ------------------------------------------------------------ | ---------------- |
| `/warn @kullanıcı [sebep]` | Kullanıcıya manuel uyarı verir.                              | Kick Members     |
| `/uyarilar @kullanıcı`     | Kullanıcının mevcut uyarılarını gösterir.                    | -                |
| `/uyarisil @kullanıcı`     | Kullanıcının uyarılarından birini siler.                     | Kick Members     |
| `/clear [sayı]`            | Belirtilen kadar mesajı siler (max 100).                     | Manage Messages  |
| `/mute @kullanıcı [süre]`  | Kullanıcıyı belirtilen süre susturur. Örn: `10s`, `1h`, `1d` | Moderate Members |
| `/unmute @kullanıcı`       | Kullanıcının susturmasını kaldırır.                          | Moderate Members |
| `/ban @kullanıcı [sebep]`  | Kullanıcıyı sunucudan yasaklar.                              | Ban Members      |

# Güvenlik & Yönetim Komutları
| Komut                                               | Açıklama                                                                 | Gereken Yetki |
| --------------------------------------------------- | ------------------------------------------------------------------------ | ------------- |
| `/logkanal #kanal`                                  | Moderasyon loglarının gönderileceği kanalı ayarlar.                      | Owner         |
| `/otorol @rol`                                      | Sunucuya yeni girenlere otomatik rol verir.                              | Owner         |
| `/op @kullanıcı`                                    | Kullanıcıyı moderasyon filtrelerinden muaf tutar (küfür, reklam, flood). | Owner         |
| `/unop @kullanıcı`                                  | Kullanıcının muafiyetini kaldırır.                                       | Owner         |
| `/durum [oynuyor/izliyor/dinliyor/yayında] [metin]` | Botun durumunu değiştirir.                                               | Owner         |

# XP & Level Sistemi
| Komut                                                                       | Açıklama                                                                | Gereken Yetki |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------- |
| `/level [kullanıcı]`                                                        | Kullanıcının XP ve level bilgisini gösterir.                            | -             |
| `/levelsistemi @rol1 @rol2 @rol3 [#kanal1] [#kanal2] [#kanal3] [#logkanal]` | Level sistemini ayarlar. Belirli level’larda rol verir ve duyuru yapar. | Owner         |
| `/level-sifirla @kullanıcı`                                                 | Kullanıcının level ve XP bilgilerini sıfırlar.                          | Owner         |

# Öneri & Oylama 
| Komut            | Açıklama                                | Gereken Yetki |
| ---------------- | --------------------------------------- | ------------- |
| `/oneri [metin]` | Bot için öneri gönderir.                | -             |
| `/oneriler`      | Sunucuya gönderilen önerileri listeler. | Owner         |
| `/oylama [soru]` | Emoji ile oylama başlatır ✅ ❌           | -             |

# Kayıt & Geçmiş
| Komut                 | Açıklama                             | Gereken Yetki |
| --------------------- | ------------------------------------ | ------------- |
| `/history @kullanıcı` | Kullanıcının mod geçmişini gösterir. | Owner         |

# Yapay Zeka 
| Komut           | Açıklama                                          |
| --------------- | ------------------------------------------------- |
| `/soru [metin]` | GPT-4 API ile etkileşime geçer ve yanıt döndürür. |


# Kurulum ve Kullanım
`git clone https://github.com/xNewt0/Modulus`
`cd Modulus`
`pip install -r requirements.txt`
`python3 bot.py`

Kurulumu tamamladıktan ve botu çalıştırdıktan sonra, sizden Bot Tokeni ile birlikte bot üzerinde en yüksek yetkiye sahip kullanıcı(lar)ın Discord ID’leri istenecektir.
Bu bilgileri doğru şekilde girerek botun sorunsuz çalışmasını sağlayabilirsiniz.

# Notlar
- Kod çalıştırıldığında veritabanı otomatik olarak oluşturulur. Eğer ismini değişmek isterseniz kodun 50. satırındaki dosya ismini değiştirebilirsiniz.
- /sarki komutundaki şarkıları değiştirmek için 1426. satırdaki kısmı değişebilirsiniz.
- /sunucu-kur komutunda oluşturulan #Kurallar kanalındaki kuralları kendinize göre özelleştirebilir, diğer oluşturulacak kanal ve rol isimlerini değiştirebilirsiniz.
- 610. satırda yasaklı kelimeler ve küfürler bulunmaktadır bir kullanıcı bu kelimeleri kullanırsa otomatik olarak uyarı alır bu kelimeleri de kendinize göre özelleştirebilirsiniz veya /op komutunu kullanarak uyarıları seçilen kullanıcı için deaktif edebilirsiniz.
- Bu araç, kullanıcıların kendi Discord botlarını çalıştırabilmeleri için geliştirilmiştir. Botun çalıştırılması için gerekli olan token, veritabanı ve diğer tüm bileşenler tamamen kullanıcının sorumluluğundadır ve uygulama yalnızca kullanıcının kendi bilgisayarında çalışır.
- Botun tüm komutları ve filtreleri düzgün çalışabilmesi için Discord sunucusuna eklerken “Administrator” yetkisi verilmelidir. Aksi halde bazı komutlar (ban, mute, rol verme vb.) çalışmayabilir.
- Eğer yeni komutlar eklediyseniz veya komutlar gözükmüyorsa /sync komutunu çalıştırarak Discord ile senkronize edebilirsiniz.
- Kodda değişiklik yaptıktan sonra botu tekrar başlatmanız gerekir.
- Bot SQLite veritabanını kullanmaktadır. Çok büyük sunucularda daha iyi performans için aiosqlite veya harici bir veritabanı tercih edilebilir.
- Bot, varsayılan olarak kendi bilgisayarınızda (local) çalıştırılacak şekilde tasarlanmıştır. Ancak dilerseniz VDS (Virtual Dedicated Server) veya bulut tabanlı bir sunucuda da çalıştırabilirsiniz. Bu sayede botunuz 7/24 kesintisiz olarak aktif kalır.
  


