import unittest
import datetime
import xml.etree.ElementTree as ET

from model.story import Story
from main import get_suggestion_for_story
from utils.story_parsing_utils import get_nf_items_from_xml_items

class StoryParsingTest(unittest.TestCase):
	def test_if_story_contains_valid_date_then_event_should_be_extracted(self):
		story = Story(
			"Norway",
			"Norway will participate in the Eurovision Song Contest 2020. Melodi Grand Prix will again be used to select the country's entrant, with the final taking place on the 15th of February.",
			"http://link.com"
		)
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 1)
		date = suggestion.dateTimesCet[0]['dateTimeCet']
		self.assertTrue(date[5:10] == "02-15")


	def test_if_story_does_not_contain_date_within_nf_season_range_then_no_event_should_be_extracted(self):
		story = Story(
			"Sweden",
			"Jan Då has won Melodifestivalen and will represent Sweden. Sweden will take part in the first semi-final on May 12.",
			"http://link"
		)
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(suggestion is None)


	def test_if_story_contains_some_valid_dates_then_associated_events_should_be_extracted(self):
		story = Story(
			"Estonia",
			"Estonia will choose their representative through Eesti Laul. The semi-finals will take place on February 8 and 10, and the final on February 22. Estonia will take part in the first semi-final on May 12.",
			"http://link"
		)
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 3)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "02-08")
		self.assertTrue(suggestion.dateTimesCet[1]['dateTimeCet'][5:10] == "02-10")
		self.assertTrue(suggestion.dateTimesCet[2]['dateTimeCet'][5:10] == "02-22")


	def test_if_story_contains_numerical_values_that_are_not_dates_these_should_not_be_extracted(self):
		story = Story(
			"France",
			"Destination Eurovision will take place on the 25th of January. Last year france was represented by Jean D'eau who won Destination Eurovision with 25% of the public vote and 155 points. He finished 16th at Eurovision 2019.",
			"http://link"
		)
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 1)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "01-25")


	def test_full_article_non_regression_testing_1(self):
		story = Story("Sweden", ".The dates and cities for the 2020 edition of Melodifestivalen have been revealed..Swedish broadcaster SVT has confirmed the dates of Melodifestivalen 2020, starting in Linköping on February 6th, and ending in Stockholm on March 13th. Tickets for all six shows will be released at 9am on October 31st..The dates are as follows:..Semi-Final 1 (Linköping) – February 6th.Semi-Final 2 (Gothenburg) – February 13th.Semi-Final 3 (Luleå) – February 20th.Semi-Final 4 (Malmö) – February 27th.Andra Chansen (Eskilstuna) – March 6th.Final (Stockholm) – March 13th....Amanda Aasa is the first artist to be revealed as participating in Melodifestivalen 2020, as she was selected by a jury through the competition P4 Nästa. Amanda will have to participate in Melodifestivalen with a different entry, as her P4 Nästa entry was released before September 1, which makes it ineligible for Eurovision..A total of 28 artists will compete in the 2020 edition of Melodifestivalen.&nbsp;This year marks the 60th anniversary of the show, and the SVT has promised that it will be “extraordinary”..Sweden finished 6th at the Grand Final of the Eurovision Song Contest 2019 in Tel Aviv, Israel. Sweden was represented by John Lundvik with the song “Too Late For Love”, and came second in the jury voting with 241 points, but came 9th in the televote with 93 points..", "https://eurovoix.com")
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 6)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "02-06")
		self.assertTrue(suggestion.dateTimesCet[1]['dateTimeCet'][5:10] == "02-13")
		self.assertTrue(suggestion.dateTimesCet[2]['dateTimeCet'][5:10] == "02-20")
		self.assertTrue(suggestion.dateTimesCet[3]['dateTimeCet'][5:10] == "02-27")
		self.assertTrue(suggestion.dateTimesCet[4]['dateTimeCet'][5:10] == "03-06")
		self.assertTrue(suggestion.dateTimesCet[5]['dateTimeCet'][5:10] == "03-13")


	def test_full_article_non_regression_testing_2(self):
		story = Story("Poland", ".Further details of the Polish selection process for Eurovision 2020, Szansa na Sukces have been revealed ahead of the filming of the semi-finals..Following the reveal of Cleo, Szpak and Gromee as the jury members for Szansa na Sukces, it has been revealed that they will not be performing in each show. This is a change from the traditional format of the show that sees one judge’s songs covered in each show. Instead the theme of the semi-finals are:..Semi-Final One – ABBA.Semi-Final Two – Eurovision Hits.Semi-Final Three – The Beatles..Five acts have also been confirmed so far as competing in the show they are:..Daj To Glosniej.Saszan – Competed in the Polish national selection in 2018.Adrian Makar – Winner of Mam talent! in 2014.Weronika Curylo – Runner up in The Voice of Poland season 7.Basia Giewont..Recording of the semi-finals for Szansa na Sukces will take place from Sunday to Monday..Szansa na Sukces will be aired every Sunday from February 2 to February 23 on TVP2 and will be hosted by Artur Orzech. The in-studio jury will select one artist from each semi-final to advance to the final. The jury will also award a Golden Ticket to one artist who did not originally qualify to also advance to the final. In the final, the artists will each perform a cover song and and original song, which will be their Eurovision entry. The winner will be chosen solely by public voting..Szansa na Sukces&nbsp;was used as the Polish national final for Junior Eurovision last year. The winner of the show, Viki Gabor, went on to win Junior Eurovision 2019, achieving Poland’s second consecutive win in the contest. This selection method is also&nbsp;likely&nbsp;to be used to select the Polish entrant for Junior Eurovision 2020..", "https://eurovoix.com")
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 4)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "02-02")
		self.assertTrue(suggestion.dateTimesCet[1]['dateTimeCet'][5:10] == "02-09")
		self.assertTrue(suggestion.dateTimesCet[2]['dateTimeCet'][5:10] == "02-16")
		self.assertTrue(suggestion.dateTimesCet[3]['dateTimeCet'][5:10] == "02-23")


	def test_full_article_non_regression_testing_3(self):
		story = Story("Finland", ".Six acts have been selected to compete in UMK 2020, as YLE announces the total number of submission received for the competition..After assessing a total of 426 submissions into UMK 2020, YLE has selected the six finalists who will be competing to represent Finland at Eurovision 2020. A jury formed of ten music professionals both inside and outside of YLE selected the six finalists..The six acts who will be competing in UMK 2020 will be revealed on January 21 live on the YLE website. UMK 2020 will be held on March 7 at the Mediapolis Studio in Tampere. The selected songs, as well the the jury members who chose them will also be revealed on January 21..This is the first time since the 2017 contest that Finland has opened UMK back up to any interested singers and songwriters. Yle had opted to internally select their singer for Eurovision, and then use UMK as a song selection show..Finland was represented by Darude feat. Sebastian Rejman with the song “Look Away” in Tel Aviv. Finland finished last in their semi-final scoring just 23 points. Finland received 14 points from the televote and 9 points from the juries.", "https://eurovoix.com")
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 2)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "01-21")
		self.assertTrue(suggestion.dateTimesCet[1]['dateTimeCet'][5:10] == "03-07")


	def test_full_article_non_regression_testing_4(self):
		story = Story("Denmark", ".Denmark will select their participant for the Eurovision Song Contest 2020 on March 7 in Copenhagen..The Danish national broadcaster has announced that Copenhagen will host the nations selection for Eurovision 2020. The Royal Arena will be the venue for next years Dansk Melodi Grand Prix, with tickets already on sale.&nbsp; The Mayor of Copenhagen said today:.The Melodi Grand Prix is ​​a special part of our cultural heritage, which year after year manages to gather the Danes across generations and parts of the country. After 17 years, we look forward to welcoming the Danish Melodi Grand Prix back in Copenhagen to a huge folk party for both young and old..DR has not yet announced the submissions process for Dansk Melodi Grand Prix 2020. An announcement is expected to take place in the weeks after this years contest in Tel Aviv has taken place..Who is Leonora?.20-year-old Leonora will be representing Denmark at the Eurovision Song Contest. Leonora is a person with many talents,&nbsp;she is a triple Danish Championship title holder in figure skating, and she has participated in both the Junior World Championship and Nordic Championship..Outside the world of sport, she decided at the age of 15 to focus on music instead, playing guitar and writing her own songs. She was then approached by Lise Cabble to perform “Love is Forever” and won the Danish selection..", "https://eurovoix.com")
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 1)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "03-07")


	def test_full_article_non_regression_testing_5(self):
		story = Story("Lithuania", ".The Lithuanian national selection process has been renamed for the first time since 2013, with the new title ‘Pabandom iš naujo’..With Lithuania revamping its national selection process for the Eurovision Song Contest, the name of the show has also been changed. The show which was previously called ‘Eurovizijos dainų konkurso nacionalinė atranka’ is now called ‘Pabandom iš naujo’ which translates as ‘We Go Again!’.Pabandom iš naujo will begin on January 11 and will run every Saturday until February 15. All shows will be presented by Gabrielė Martirosian, Giedrius Masalskis and Ieva Zasimauskaitė, who represented&nbsp;Lithuania in 2018. The first three shows will be elimination heats where half the acts will be eliminated. Next, there will be two semi-finals, where four songs will qualify from each show. In the final, eight songs will participate..The results in each round will be decided by a combination of in-studio jury voting (50%) and public voting (50%). The voting process for the jury has changed. The jury will no longer comment on all performances and will view the performances in a separate space outside the studio. In addition, the public vote will no longer be shown during the show, with the results only known at the end of the show. In case of a tie, the jury vote will take preference. The rules of the selection are subject to change at any time..LRT has also committed to spending additional funds on the winning act from the selection process. The broadcaster will commit to spending on stage effects, directing, vocal lessons, costumes and more..", "https://eurovoix.com")
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 6)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "01-11")
		self.assertTrue(suggestion.dateTimesCet[1]['dateTimeCet'][5:10] == "01-18")
		self.assertTrue(suggestion.dateTimesCet[2]['dateTimeCet'][5:10] == "01-25")
		self.assertTrue(suggestion.dateTimesCet[3]['dateTimeCet'][5:10] == "02-01")
		self.assertTrue(suggestion.dateTimesCet[4]['dateTimeCet'][5:10] == "02-08")
		self.assertTrue(suggestion.dateTimesCet[5]['dateTimeCet'][5:10] == "02-15")


	def test_full_article_non_regression_testing_6(self):
		story = Story('Armenia', ".Armenia is set to select its participant for the Eurovision Song Contest 2020 on February 15..AMPTV has announced today that the final of Depi Evratesil 2020 will take place on February 15. The broadcaster has not confirmed the acts competing in the Armenian selection process, but has confirmed that they have all now been chosen. The past few days has seen a jury assess all of the submitted songs to select those that will compete in the final on February 15..Depi Evratesil has been used as the Armenian national final on two previous occasions. In 2017, it was used to find the artist for Eurovision with the song being internally selected at a later date. In 2018, artists were able to submit original songs. After Sevak Khanagyan failed to qualify for the final of Eurovision 2018, an internal selection was used for 2019..In 2019, Srbuk was internally selected to represent Armenia in Tel Aviv. She finished 16th in the second semi-final with “Walking Out”, bringing Armenia their worst result to date in the contest..Source: AMPTV.Armenia in the Eurovision Song Contest  Armenia debuted in the Eurovision Song Contest in 2006 and has participated every year since, excluding 2012. Armenia’s best results came in 2008 and 2014 when they finished 4th in the final. They have twice failed to qualify for the final. The first time was in 2011, when Emmy finished in 12th with “Boom Boom”. She was 1 point away from qualifying for the final. In 2019, Srbuk finished 16th in her semi-final with “Walking Out”, bringing Armenia their worst result to date in the contest.  ..Tags: Depi Evratesil	Share this:Click to share on Twitter (Opens in new window)Click to share on Facebook (Opens in new window)Click to print (Opens in new window)Click to share on LinkedIn (Opens in new window)Click to share on Reddit (Opens in new window)Click to share on Tumblr (Opens in new window)Click to share on Pinterest (Opens in new window)Click to share on Pocket (Opens in new window)Click to share on Telegram (Opens in new window)Click to share on WhatsApp (Opens in new window)Click to share on Skype (Opens in new window)Click to email this to a friend (Opens in new window)......	..Posted by:Anthony GrangerSince launching Eurovoix in April 2011, it has been a pleasure to find out more about this amazing continent through the Eurovision Family of Events. From starting out as a small site, it's been brilliant to see the site grow and flourish and continue to bring our readers everything from the world of Eurovision.	....", "https://eurovoix.com")
		suggestion = get_suggestion_for_story(story, datetime.datetime(2020, 9, 1, 0, 0, 0))
		self.assertTrue(len(suggestion.dateTimesCet) == 1)
		self.assertTrue(suggestion.dateTimesCet[0]['dateTimeCet'][5:10] == "02-15")


	def test_if_xml_items_include_items_with_national_selection_category_then_should_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>First item</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<content>Content</content>
				</item>
				<item>
					<title>Second item</title>
					<link>https://eurovoix.com/</link>
					<category>Random category</category>
					<content>Content</content>
				</item>
				<item>
					<title>Third item</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')

		nf_items = get_nf_items_from_xml_items(items, [])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 2)
		self.assertTrue(titles[0] == "First item")
		self.assertTrue(titles[1] == "Third item")

	def test_if_xml_items_include_items_without_national_selection_category_but_with_nf_name_in_title_then_should_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>Sweden: Melodifestivalen final on March 13</title>
					<link>https://eurovoix.com/</link>
					<category>Sweden</category>
					<content>Content</content>
				</item>
				<item>
					<title>Second item</title>
					<link>https://eurovoix.com/</link>
					<category>Random category</category>
					<content>Content</content>
				</item>
				<item>
					<title>Latvia: Supernova submission window open</title>
					<link>https://eurovoix.com/</link>
					<category>Eurovision</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')
		
		nf_items = get_nf_items_from_xml_items(items, ['melodifestivalen', 'supernova'])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 2)
		self.assertTrue(titles[0] == "Sweden: Melodifestivalen final on March 13")
		self.assertTrue(titles[1] == "Latvia: Supernova submission window open")

	def test_if_xml_items_include_items_with_unwanted_categories_then_should_not_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>Ireland: Junior Eurovision selection on October 30</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<category>Junior Eurovision Song Contest</category>
					<content>Content</content>
				</item>
				<item>
					<title>Sweden: EYM selection on February 1</title>
					<link>https://eurovoix.com/</link>
					<category>Eurovision Young Musicians</category>
					<category>National Selection</category>
					<content>Content</content>
				</item>
				<item>
					<title>Sweden: Lilla Melodifestivalen final on October 15</title>
					<link>https://eurovoix.com/</link>
					<category>National Selection</category>
					<category>Junior Eurovision Song Contest</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')
		
		nf_items = get_nf_items_from_xml_items(items, ['melodifestivalen'])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 0)

	def test_if_xml_items_include_items_without_national_selection_category_but_with_nf_name_or_alt_name_in_title_then_should_return_them(self):
		xml_items = """
			<items>
				<item>
					<title>Sweden: Melfest final on March 13</title>
					<link>https://eurovoix.com/</link>
					<category>Sweden</category>
					<content>Content</content>
				</item>
				<item>
					<title>Finland: UMK 2021 opens submission window</title>
					<link>https://eurovoix.com/</link>
					<category>Random category</category>
					<content>Content</content>
				</item>
			</items>
		""".replace('\n', '').replace('\t', '')
		root = ET.fromstring(xml_items)
		items = root.findall('item')
		
		nf_items = get_nf_items_from_xml_items(items, ['melodifestivalen', 'melfest', 'umk', 'uuden musiikin kilpailu'])
		titles = list(map(lambda i: i.find('title').text, nf_items))
		self.assertTrue(len(nf_items) == 2)
		self.assertTrue(titles[0] == "Sweden: Melfest final on March 13")
		self.assertTrue(titles[1] == "Finland: UMK 2021 opens submission window")
