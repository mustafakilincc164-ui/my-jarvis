import re

# Türkçe karakter duyarlı küçük harfe çevirme
def turkish_lower(text: str) -> str:
    """Türkçe karakterleri doğru şekilde küçük harfe çevirir."""
    text = text.replace('İ', 'i').replace('I', 'ı')
    return text.lower()

# Basit tokenization (kelimelere bölme)
def tokenize(sentence: str) -> list[str]:
    """Cümleyi kelimelere böler, noktalama işaretlerini temizler."""
    sentence = turkish_lower(sentence)
    # Sadece harfler, sayılar ve boşlukları tut, noktalama işaretlerini kaldır
    clean_sentence = re.sub(r'[^\w\s]', '', sentence)
    return clean_sentence.split()

# Basit kök bulma / temizleme (Ek atma)
def stem(word: str) -> str:
    """Türkçe kelime eklerini basitçe temizler. 
    İleri düzey bir kütüphane yerine, kelime eşleşmelerini artırmak için basit kurallar kullanır.
    """
    word = turkish_lower(word)
    # Çok temel çoğul, yönelme, bulunma eklerini temizleyelim
    suffixes = ['ler', 'lar', 'da', 'de', 'ta', 'te', 'dan', 'den', 'tan', 'ten', 'yi', 'yı', 'yu', 'yü', 'ın', 'in', 'un', 'ün', 'ım', 'im', 'um', 'üm']
    
    # Kelime çok kısa değilse ekleri kontrol et
    if len(word) > 4:
        for suffix in suffixes:
            if word.endswith(suffix):
                # Eki kaldır ve kelime boyu 3'ten büyük kalıyorsa o haliyle dön
                stemmed = word[:-len(suffix)]
                if len(stemmed) >= 3:
                    return stemmed
    return word

def bag_of_words(tokenized_sentence: list[str], all_words: list[str]) -> list[float]:
    """Tokenize edilmiş cümledeki kelimelerin, tüm kelimeler listesindeki varlığını 
    1 ve 0'lardan oluşan bir vektör olarak döner.
    """
    # Her bir kelimeyi kök haline getir
    sentence_words = [stem(w) for w in tokenized_sentence]
    
    bag = [0.0] * len(all_words)
    for idx, w in enumerate(all_words):
        if w in sentence_words:
            bag[idx] = 1.0
            
    return bag

# Test kısmı (Script doğrudan çalıştırılırsa çalışır)
if __name__ == "__main__":
    test_sentence = "Jarvis, not defterini hemen açabilir misin?"
    tokens = tokenize(test_sentence)
    print("Tokens:", tokens)
    
    stems = [stem(w) for w in tokens]
    print("Stems:", stems)
    
    words = ["jarvis", "not", "defter", "aç", "saat", "hava"]
    bag = bag_of_words(tokens, words)
    print("Bag of Words:", bag)
