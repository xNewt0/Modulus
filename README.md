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

# Moderasyon Komutları
| Komut                      | Açıklama                                     | Yetki            |
| -------------------------- | -------------------------------------------- | ---------------- |
| `/warn @kullanıcı [sebep]` | Kullanıcıya manuel uyarı verir.              | Kick Members     |
| `/uyarilar @kullanıcı`     | Kullanıcının mevcut uyarı sayısını gösterir. | -                |
| `/uyarisil @kullanıcı`     | Kullanıcının bir uyarısını siler.            | Kick Members     |
| `/clear [sayı]`            | Belirtilen sayıda mesajı siler (max 100).    | Manage Messages  |
| `/mute @kullanıcı [süre]`  | Kullanıcıyı belirtilen süre susturur.        | Moderate Members |
| `/unmute @kullanıcı`       | Kullanıcının susturmasını kaldırır.          | Moderate Members |
| `/ban @kullanıcı [sebep]`  | Kullanıcıyı sunucudan yasaklar.              | Ban Members      |

# Yönetim & Güvenlik
| Komut                  | Açıklama                                                  | Yetki |
| ---------------------- | --------------------------------------------------------- | ----- |
| `/logkanal #kanal`     | Log kanalını ayarlar.                                     | Owner |
| `/logs @kullanıcı`     | Kullanıcının mesaj loglarını gösterir.                    | Owner |
| `/history @kullanıcı`  | Kullanıcının moderasyon geçmişini gösterir.               | Owner |
| `/otorol @rol`         | Sunucuya yeni katılanlara otomatik rol verir.             | Owner |
| `/op @kullanıcı`       | Kullanıcıyı küfür/reklam/flood filtrelerinden muaf tutar. | Owner |
| `/unop @kullanıcı`     | Kullanıcının muafiyetini kaldırır.                        | Owner |
| `/sunucu-kur`          | Sunucu için temel yapıyı (kanallar, roller vb.) kurar.    | Owner |
| `/durum [tür] [metin]` | Botun durum mesajını değiştirir.                          | Owner |
| `/sync`                | Slash komutlarını senkronize eder.                        | Owner |

# Level Sistemi
| Komut                                                                  | Açıklama                                          | Yetki |
| ---------------------------------------------------------------------- | ------------------------------------------------- | ----- |
| `/level [kullanıcı]`                                                   | Kullanıcının level ve XP bilgisini gösterir.      | -     |
| `/levelsistemi @rol1 @rol2 @rol3 [#kanal1] [#kanal2] [#kanal3] [#log]` | Level sistemini ayarlar (roller, duyurular, log). | Owner |
| `/level-sifirla @kullanıcı`                                            | Kullanıcının level ve XP bilgisini sıfırlar.      | Owner |

# Genel Komutlar
| Komut                    | Açıklama                                             |
| ------------------------ | ---------------------------------------------------- |
| `/ping`                  | Botun gecikmesini (ms) gösterir.                     |
| `/avatar [kullanıcı]`    | Belirtilen kullanıcının avatarını gösterir.          |
| `/kullanici [kullanıcı]` | Kullanıcı hakkında bilgi verir.                      |
| `/sunucu`                | Sunucu hakkında genel bilgileri gösterir.            |
| `/zar [üst sınır]`       | 1 ile belirtilen üst sınır arasında zar atar.        |
| `/sarki`                 | Rastgele bir şarkı önerir.                           |
| `/afk [mesaj]`           | AFK moduna geçer. Etiketlenince özel mesaj gösterir. |
| `/yetkilerim`            | Sunucudaki yetkilerinizi listeler.                   |
| `/yardim`                | Tüm komutlar ve açıklamalarını gösterir.             |

# Öneri & Oylama
| Komut            | Açıklama                                |
| ---------------- | --------------------------------------- |
| `/oylama [soru]` | Emojiyle oylama başlatır.               |
| `/oneri [metin]` | Öneri gönderir.                         |
| `/oneriler`      | Sunucuya gönderilen önerileri listeler. |

# Yapay Zeka 
| Komut           | Açıklama                            |
| --------------- | ----------------------------------- |
| `/soru [metin]` | GPT-4 API üzerinden yanıt döndürür. |


# Kurulum ve Kullanım
`git clone https://github.com/xNewt0/Modulus && cd Modulus && pip install -r requirements.txt && python3 bot.py`


Kurulumu tamamladıktan ve botu çalıştırdıktan sonra, sizden Bot Tokeni ile birlikte bot üzerinde en yüksek yetkiye sahip kullanıcı(lar)ın Discord ID’leri istenecektir.
Bu bilgileri doğru şekilde girerek botun sorunsuz çalışmasını sağlayabilirsiniz.

# Notlar
- Kod çalıştırıldığında veritabanı otomatik olarak oluşturulur. Eğer ismini değişmek isterseniz kodun 50. satırındaki dosya ismini değiştirebilirsiniz.
- /sarki komutundaki şarkıları değiştirmek için 1426. satırdaki kısmı değişebilirsiniz.
- /sunucu-kur komutunda oluşturulan #Kurallar kanalındaki kuralları kendinize göre özelleştirebilir, diğer oluşturulacak kanal ve rol isimlerini değiştirebilirsiniz.
- Kodun 610. satırıda yasaklı kelimeler ve küfürler bulunmaktadır bir kullanıcı bu kelimeleri kullanırsa otomatik olarak uyarı alır bu kelimeleri de kendinize göre özelleştirebilirsiniz veya /op komutunu kullanarak uyarıları seçilen kullanıcı için deaktif edebilirsiniz.
- Bu araç, kullanıcıların kendi Discord botlarını çalıştırabilmeleri için geliştirilmiştir. Botun çalıştırılması için gerekli olan token, veritabanı ve diğer tüm bileşenler tamamen kullanıcının sorumluluğundadır ve uygulama yalnızca kullanıcının kendi bilgisayarında çalışır.
- Botun tüm komutları ve filtreleri düzgün çalışabilmesi için Discord sunucusuna eklerken “Administrator” yetkisi verilmelidir. Aksi halde bazı komutlar (ban, mute, rol verme vb.) çalışmayabilir.
- Eğer yeni komutlar eklediyseniz veya komutlar gözükmüyorsa /sync komutunu çalıştırarak Discord ile senkronize edebilirsiniz.
- Kodda değişiklik yaptıktan sonra botu tekrar başlatmanız gerekir.
- Bot SQLite veritabanını kullanmaktadır. Çok büyük sunucularda daha iyi performans için aiosqlite veya harici bir veritabanı tercih edilebilir.
- Bot, varsayılan olarak kendi bilgisayarınızda (local) çalıştırılacak şekilde tasarlanmıştır. Ancak dilerseniz VDS (Virtual Dedicated Server) veya bulut tabanlı bir sunucuda da çalıştırabilirsiniz. Bu sayede botunuz 7/24 kesintisiz olarak aktif kalır.
- Bana Discord üzerinden ulaşabilirsiniz thenewt00
  


