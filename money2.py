# coding: utf-8

import tabula
import datetime
import pandas as pd

class pdf:
    def __init__(self, pdf_name):
        # Read pdf into list of DataFrame
        self.listDf = []
        self.OperationFiltered = []
        pages = tabula.read_pdf(pdf_name, pages='all')
        for page in pages: self.dealPage(page)
        self.to_OFX(pdf_name.replace('.pdf','.ofx'))

        fout1 = open('filtered', "w")
        fout1.write('\n'.join(self.OperationFiltered))
        fout1.close()

    def dealPage(self, df):
        df = df.reset_index()
        if len(df.columns) > 4:
            df.rename(columns={ df.columns[1]: "Date", df.columns[2]: "Label", df.columns[3]: "Label2", df.columns[-1]: "Montant" }, inplace = True)
            df2 = pd.DataFrame()

            for i in range(len(df)) :
                if self.getDate(df.loc[i, "Date"]) != ['NaN', 'NaN']:
                    dates = self.getDate(df.loc[i, "Date"])
                    if self.getDate(df.loc[i, "Label"]) == ['NaN', 'NaN']:
                        df2 = df2.append({'date_transaction' : dates[0], 'date_valeur' : dates[1], 'Label' : df.loc[i, "Label"], 'montant' :self.getAmount(df.iloc[i])}, ignore_index=True)
                        # print(27,df.loc[i])
                        # print(28, self.getDate(df.loc[i, "Label"]), dates[0], dates[1], df.loc[i, "Label"], self.getAmount(df.iloc[i]))
                    else:
                        print(30,df.loc[i])
                        print(31, self.getDate(df.loc[i, "Label"]))
                        df2 = df2.append({'date_transaction' : dates[0], 'date_valeur' : dates[1], 'Label' : df.loc[i, "Label"], 'montant' :self.getAmount(df.iloc[i])}, ignore_index=True)
                        input()
                else:
                    # print(33, 'not considering this operation')
                    self.OperationFiltered.append(str(df.loc[i]))
            self.listDf.append(df2)
        # else:
                    # self.OperationFiltered.append(str(df.loc[i]))
        input()

    def getMonth(self, smonth):
        if smonth == "déc": return 12
        elif smonth == "jan": return 1
        elif smonth == "fév": return 2
        elif len(smonth) > 3: return 'N/A'
        else:
            print(37, smonth)
            input()
            return 'N/A'

    def getAmount(self, lyne):
        for item in reversed(lyne.tolist()):
            if (str(item) != 'nan') and (str(item) != 'CR'): return float(item.replace(' ','').replace(',','.'))
        return 'N/A'

    def getDate(self, lyne):
        val = str(lyne).split(' ')
        if ('Date de' not in str(lyne)) and ('rations pour' not in str(lyne)) and ('transaction' not in str(lyne)) and ('Carte xxxx' not in str(lyne)):
            try:
                if len(val) == 4:
                    date_stock=datetime.datetime(2020, self.getMonth(val[1]), int(val[0]))
                    date_valeur=datetime.datetime(2020, self.getMonth(val[3]), int(val[2]))
                    return [date_stock.strftime("%m/%d/%Y"), date_valeur.strftime("%m/%d/%Y")]
                elif len(val) == 2:
                    date_stock=datetime.datetime(2020, self.getMonth(val[1]), int(val[0]))
                    return [date_stock.strftime("%m/%d/%Y"), date_stock.strftime("%m/%d/%Y")]
                elif str(lyne) == 'nan': return ['NaN', 'NaN']
                elif len(val) > 4: return ['NaN', 'NaN']
                else:
                    # print(70, str(lyne))
                    return ['NaN','NaN']
            except:
                return ['NaN', 'NaN']
        else:
            return  ['NaN', 'NaN']

    def ope_to_OFX(self, date_transaction, label, montant):
        buff = []
        buff.append('<STMTTRN>')
        if montant > 0: buff.append('<TRNTYPE>CREDIT')
        else: buff.append('<TRNTYPE>DEBIT')
        val = date_transaction.split('/')
        yyyy = val[2].strip()
        mm = val[1].strip()
        dd = val[0].strip()
        buff.append('<DTPOSTED>' + str(yyyy) + str(mm) + str(dd))
        buff.append('<TRNAMT>' + str(montant))
        buff.append('<FITID>')
        buff.append('<NAME>' + str(label))
        buff.append('</STMTTRN>')
        return buff

    def header(self):
        return ['Content-Type: application/x-ofx', 'OFXHEADER:100', 'DATA:OFXSGML', 'VERSION:102', 'SECURITY:NONE', 'ENCODING:USASCII', 'CHARSET:1252', 'COMPRESSION:NONE', 'OLDFILEUID:NONE', 'NEWFILEUID:NONE', '<OFX>', '<SIGNONMSGSRSV1>', '<SONRS>', '<STATUS>', '<CODE>0', '<SEVERITY>INFO', '</STATUS>', '<DTSERVER>20200309130000', '<LANGUAGE>FRA', '<DTPROFUP>20200309130000', '<DTACCTUP>20200309130000', '</SONRS>', '</SIGNONMSGSRSV1>','<BANKMSGSRSV1>','<STMTTRNRS>','<TRNUID>00','<STATUS>','<CODE>0','<SEVERITY>INFO','</STATUS>','<STMTRS>','<CURDEF>EUR','<BANKACCTFROM>','<BANKID>30002','<BRANCHID>00675','<ACCTID>022152Z','<ACCTTYPE>CHECKING','</BANKACCTFROM>','<BANKTRANLIST>','<DTSTART>20200217120000','<DTEND>20200306120000']

    def tail(self, buff):
        buff.append('</BANKTRANLIST>')
        buff.append('<LEDGERBAL>')
        buff.append('<BALAMT>+829.43')
        buff.append('<DTASOF>20200306120000')
        buff.append('</LEDGERBAL>')
        buff.append('<AVAILBAL>')
        buff.append('<BALAMT>+829.43')
        buff.append('<DTASOF>20200306120000')
        buff.append('</AVAILBAL>')
        buff.append('</STMTRS>')
        buff.append('</STMTTRNRS>')
        buff.append('</BANKMSGSRSV1>')
        buff.append('</OFX>')
        return buff

    def to_OFX(self, fyle_out):
        ofx = self.header()
        for df in self.listDf:
            for i in range(len(df)) :
                print('to_OFX', df.loc[i, "date_transaction"], df.loc[i, "date_valeur"], df.loc[i, "Label"], df.loc[i, "montant"])
                ofx = ofx + self.ope_to_OFX(df.loc[i, "date_transaction"], df.loc[i, "Label"], df.loc[i, "montant"])
        ofx = self.tail(ofx)
        
        fout1 = open(fyle_out, "w")
        fout1.write('\n'.join(ofx))
        fout1.close()

if __name__ == '__main__':
    ofx = pdf("test.pdf")



