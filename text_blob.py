from textblob import TextBlob


blob = TextBlob(dracula)

print(blob.sentiment)

# dracula_chapters = dracula.split('CHAPTER ')

# dracula_dict = {}

# for count, chapter in enumerate(dracula_chapters):
#     if count == 0:
#         continue
#     chapter_num = chapter.split('\n', 1)
#     dracula_dict['CHAPTER ' + chapter_num[0]] = chapter


# for item in dracula_dict:
#     print(f'{item}\n\n{dracula_dict[item][0:25]}')
