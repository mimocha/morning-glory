import random

dow_th = {
	1: "วันจันทร์",
	2: "วันอังคาร",
	3: "วันพุธ",
	4: random.choice(["วันพฤหัสบดี", "วันพฤหัส"]),
	5: "วันศุกร์",
	6: "วันเสาร์",
	7: "วันอาทิตย์",
}


__color_otd = {
	1: "yellow",
	2: "pink",
	3: "green",
	4: "orange",
	5: "blue",
	6: "violet",
	7: "red",
}
get_color = lambda x: __color_otd[x]


__objects = [
	"flower",
	"landscape",
	"food",
	"architecture",
	"sports",
	"festival"
]
get_obj = lambda: random.choice(__objects)


__greet_a =	[
	"สวัสดี",
	"อรุณสวัสดิ์",
	"สุขสันต์"
]
__greet_b = [
	"",
	" เช้า",
	" วันนี้",
	"ยามเช้า "
]
greetings = lambda: random.choice(__greet_a) + random.choice(__greet_b)


__bless_verb = [
	"ขอให้",
	"อวยพรให้",
	"ขอให้ท่าน"
]
__bless_object = [
	"วันนี้เป็นวันที่ดี",
	"มีความสุขมากๆ",
	"สุขกาย สุขใจ",
	"สบายกาย สบายใจ",
	"มีชีวิตชีวา แจ่มใส",
	"สดชื่น แจ่มใส",
	"แจ่มใส ร่าเริง",
	"เฮงๆ ร่ำรวย",
	"โชคดี มีความสุข",
	"โชคดี มีชัย",
	"สมปรารถนา",
	"มั่งมีศรีสุข",
	"วันนี้สดใส",
	"ร่างกายแข็งแรง",
	"จิตใจผ่องใส",
	"สุขภาพแข็งแรง",
	"ปลอดโรคภัย",
]
blessings = lambda: random.choice(__bless_verb) + random.choice(__bless_object)


__fonts_list = [
	"Chakra+Petch",
	"Charm",
	"Charmonman",
	"Itim",
	"Krub",
	"Mali",
	"Maitree",
	"Mitr",
	"Pattaya",
	"Pridi",
	"Prompt",
	"Sriracha",
	"Taviraj"
]
font = lambda: random.choice(__fonts_list)


text_fill = {
	1: (247, 225, 27), # Mon
	2: (242, 160, 236), # Tue
	3: (84, 230, 62), # Wed
	4: (250, 182, 25), # Thur
	5: (133, 187, 255), # Fri
	6: (215, 52, 247), # Sat
	7: (242, 46, 66) # Sun
}