from Levenshtein import ratio 
import csv
import simplejson as json

donationsFile = open("donations.json")
donations = json.load(donationsFile)
donsTotalFile = open("donationstotal.json")
donsTotal = json.load(donsTotalFile)
recipientsFile = open("recipients.json")
recipients = json.load(recipientsFile)
recTotalsFile = open("recipienttotal.json")
recTotals = json.load(recTotalsFile)

#Shows matches of donor and recipient but not amount

donorMatchedKeys = ["DonorClientNm","DonorAddressLine1","RecipientClientNm","AmountPaid","AmountReceived"]
donorMatchedNotAmt = []

print "Writing donors that match recipient statements, but not amounts"

for donation in donations:
	for recipient in recipients:
		recipMatch = ratio(donation["RecipientClientNm"], recipient["Recipient"])
		donMatch = ratio(donation["DonorClientNm"], recipient["PayerClientNm"])
		match = recipMatch + donMatch
		if match > 1.8:
			if donation["AmountPaid"] != recipient["AmountReceived"]:
				recipientDict = {"AmountReceived":recipient["AmountReceived"]}
				donorMatchedNotAmt.append(dict(donation.items() + recipientDict.items()))

with open('matched-donor-but-not-amount.csv', 'w') as csvoutput:
	dict_writer = csv.DictWriter(csvoutput, donorMatchedKeys)
	dict_writer.writer.writerow(donorMatchedKeys)
	dict_writer.writerows(donorMatchedNotAmt)	

#Shows matches of donor and recipient but not total amount

donorTotalMatchedKeys = ["DonorClientNm","MatchedDonor","DonorAddressLine1","RecipientClientNm","MatchedRecipient","AmountPaid","Total","TotalReceived"]
donorTotalMatchedNotAmt = []

print "Writing donors that match recipient statements, but not total amounts"

for total in donsTotal:
	for recTotal in recTotals:
		recipMatch = ratio(total["RecipientClientNm"], recTotal["Recipient"])
		donMatch = ratio(total["DonorClientNm"], recTotal["PayerClientNm"])
		match = recipMatch + donMatch
		if donMatch > 0.9:
			if total["AmountPaid"] != recTotal["TotalReceived"]:
				recipientDict = {"MatchedDonor":recTotal["PayerClientNm"],"MatchedRecipient":recTotal["Recipient"],"TotalReceived":recTotal["TotalReceived"]}							
				donorTotalMatchedNotAmt.append(dict(total.items() + recipientDict.items()))

with open('matched-donor-but-not-total-amount.csv', 'w') as csvoutput:
	dict_writer = csv.DictWriter(csvoutput, donorTotalMatchedKeys)
	dict_writer.writer.writerow(donorTotalMatchedKeys)
	dict_writer.writerows(donorTotalMatchedNotAmt)	


matchKeys = ["PayerClientNm","matchedName","PayerAddressLine1","Recipient","ReceiptTyDs","matchedAmount","AmountReceived","donorAmount"]
matches = []
highestRatio = 0
highestMatch = ""


def searchRecipients(donorName,amountPaid):
	global highestRatio
	global highestMatch
	highestRatio = 0
	highestMatch = ""
	for recipient in recipients:
		match = ratio(donorName.lower(), recipient["PayerClientNm"].lower())
		if match > highestRatio:
			highestRatio = match
			highestMatch = recipient["PayerClientNm"]

		if match > 0.8:
			matchedName = {"matchedName":donorName}
			if amountPaid == recipient["AmountReceived"]:
				matchedAmount = {"matchedAmount":"yes","donorAmount":amountPaid}
			else:
				matchedAmount = {"matchedAmount":"no","donorAmount":amountPaid}	
			totalDict = dict(recipient.items() + matchedName.items() + matchedAmount.items())
			matches.append(totalDict)
			return "found"	

mismatches = []
mismatchKeys = ["RecipientClientNm","DonorClientNm","AmountPaid"]

#Check for aggregate donations declared by donors but not by parties over 12400

aggMismatches = []
aggMismatchKeys = ["RecipientClientNm","DonorClientNm","DonorAddressLine1","Total","AmountPaid","closestName","highestRatio"]

for donation in donsTotal:
	searchResult = searchRecipients(donation["DonorClientNm"],donation["AmountPaid"])
	if searchResult == "found":
		print "found"
	else:
		if donation["AmountPaid"] > 12400:
			closestMatch = {"closestName":highestMatch,"highestRatio":highestRatio}
			aggMismatches.append(dict(donation.items() + closestMatch.items()))
			

	with open('aggregate-donors-missing-from-recipients.csv', 'w') as csvoutput:
		dict_writer = csv.DictWriter(csvoutput, aggMismatchKeys)
		dict_writer.writer.writerow(aggMismatchKeys)
		dict_writer.writerows(aggMismatches)		

	with open('aggregate-donors-matches.csv', 'w') as csvoutput:
		dict_writer = csv.DictWriter(csvoutput, matchKeys)
		dict_writer.writer.writerow(matchKeys)
		dict_writer.writerows(matches)

donationsFile.close()
donsTotalFile.close()
recipientsFile.close()
recTotalsFile.close()	