# cfpb_quality-control-standards-for-avm-small-entity-compliance-guide_2024-10

 
 
                                                       
CONSUMER FINANCIAL PROTECTION BUREAU   |  OCTOBER 2024    
Quality Control Standards 
for Automated Valuation 
Models 
Small Entity Compliance Guide 


 
 
1 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
Version Log 
The CFPB updates this guide on a periodic basis.  Below is a version log noting the history of this 
document:  
 
 
Date 
Version 
Summary of Changes 
October 
2024 
1.0 
Original version 


 
 
2 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
Table of contents 
Version Log ................................................................................................................. 1 
Table of contents......................................................................................................... 2 
1. Introduction ............................................................................................................. 3 
1.1 
Scope of this guide .................................................................................... 4 
1.2 
Use of examples ........................................................................................ 4 
1.3 
Additional resources ................................................................................. 4 
2. Covered transactions ........................................................................................... 6 
2.1 
Automated valuation model ..................................................................... 6 
2.2 
Credit decisions regarding mortgages ...................................................... 6 
2.3 
Covered securitization determinations regarding mortgage-backed 
securities ................................................................................................... 9 
3. Covered persons ................................................................................................ 11 
3.1 
Secondary market issuer ......................................................................... 11 
3.2 
Mortgage originator ................................................................................. 11 
4. Quality control standards .................................................................................. 15 
5. Effective date ...................................................................................................... 17 
 


 
 
3 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
1. Introduction 
In 2010, Congress enacted the Dodd-Frank Wall Street Reform and Consumer Protection Act, 
Pub. L. 111-203, 124 Stat. 1376, 2004 (2010) (Dodd-Frank Act).  The Dodd-Frank Act amended 
the Financial Institutions Reform, Recovery, and Enforcement Act of 1989 (FIRREA) to add a 
new section 1125 relating to quality control standards for automated valuation models (AVMs) 
used to value principal dwellings securing mortgage loans.  Section 1125 directed the federal 
banking agencies,1 the National Credit Union Administration (NCUA), the Federal Housing 
Finance Agency (FHFA), and the Consumer Financial Protection Bureau (CFPB) to issue 
regulations to implement quality control standards for AVMs.   
In June 2023, the CFPB and other agencies jointly issued a notice of a proposed rulemaking, 
and in July 2024, they issued a final rule.2  Under the final rule, both mortgage originators that 
engage in credit decisions regarding certain mortgages and secondary market issuers that 
engage in securitization determinations regarding certain mortgage-backed securities must 
adopt and maintain policies, practices, procedures, and control systems to ensure that the AVMs 
they use in their respective decisions and determinations adhere to certain quality control 
standards. 
The final rule is an interagency rule.  FIRREA, as amended by the Dodd-Frank Act, provides that 
the final rule will be enforced by the banking agencies and the NCUA with respect to insured 
banks, savings associations, and credit unions, as well as federally regulated subsidiaries under 
their ownership and control.3  The statute gives the CFPB, as well as the Federal Trade 
Commission and State attorneys general, enforcement authority with respect to other 
nondepository participants in the market.4  While the final rule adds substantially similar 
provisions to each of the rulemaking agencies’ existing regulations, this guide cites solely to the 
CFPB’s regulation.5   
 
1 The federal banking agencies are the Office of the Comptroller of Currency, Federal Deposit Insurance Corporation, 
and Federal Reserve Board. 
2 89 Fed. Reg. 64658- 64580 (Aug. 7, 2024). 
3 12 U.S.C. 3354(c).  See also 12 U.S.C. 3350(6) (defining “Federal financial institutions regulatory agencies”) and (7) 
(defining “financial institution”).   
4 12 U.S.C. 3354(c). Unlike the CFPB, the Federal Trade Commission and State attorneys general do not have FIRREA 
section 1125 rulemaking authority.  12 U.S.C. 3354(b). 
5 While the CFPB is codifying its AVM requirements in Regulation Z, 12 CFR part 1026, which generally implements 
the Truth in Lending Act (TILA), the statutory authority for this final rule is FIRREA rather than TILA. 


 
 
4 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
1.1 Scope of this guide 
This guide includes a detailed summary of the final rule’s requirements.6  Except when 
specifically needed to explain the final rule, this guide does not discuss other laws, regulations, 
or regulatory guidance that may apply.  The content of this guide does not include any rules, 
bulletins, guidance, or other interpretations issued or released after the date on the guide’s cover 
page.   
Users of this guide should review the final rule as well as this guide.  The final rule is available 
on the CFPB’s website at https://www.consumerfinance.gov/rules-policy/final-rules/quality-
control-standards-for-automated-valuation-models/. 
1.2 Use of examples 
This guide has examples to illustrate some portions of the final rule.  The examples do not 
include all possible factual situations that could illustrate a particular provision, trigger a 
particular obligation, or satisfy a particular requirement.   
1.3 Additional resources 
Additional resources to help industry understand and comply with the final rule are available on 
the CFPB’s website at https://www.consumerfinance.gov/compliance/compliance-
resources/mortgage-resources/quality-control-standards-for-automated-valuation-models/.  
There is a link on this website to sign up for an email distribution list that the CFPB will use to 
announce additional resources as they become available.   
If you have a specific regulatory question about the final rule after reviewing these resources, 
you can submit the question to the CFPB on its website at 
http://reginquiries.consumerfinance.gov.  CFPB staff provides only informal responses to 
regulatory inquiries, and the responses are not official interpretations or legal advice.  CFPB 
staff is not able to respond to specific inquiries within a particular requested timeframe.  Actual 
 
6  This guide meets the requirements of section 212 of the Small Business Regulatory Enforcement Fairness Act of 
1996 with regard to the final rule and is a Compliance Aid issued by the Consumer Financial Protection Bureau.  
The CFPB published a Policy Statement on Compliance Aids, available at www.consumerfinance.gov/policy-
compliance/final rulemaking/final rules/policy-statement-compliance-aids/, that explains the CFPB’s approach to 
Compliance Aids. 


 
 
5 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
response times will vary based on the number of questions that staff is handling and the amount 
of research needed to respond to a specific question.  


 
 
6 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
2.  Covered transactions 
The final rule applies to the use of AVMs in determining the value of a consumer’s principal 
dwelling in connection with making a credit decision regarding a mortgage or covered 
securitization determination regarding a mortgage-
backed security.  However, the final rule does not 
apply to the use of AVMs in:  
1. Monitoring of the quality or performance of 
mortgages or mortgage-backed securities;  
2. Reviews of the quality of already completed 
determinations of the value of collateral; or 
3. The development of an appraisal by a certified 
or licensed appraiser as defined in 
§ 1026.35(c)(1)(i). 
12 CFR 1026.42(i)(1). 
2.1 Automated valuation model 
For purposes of the final rule, an “automated valuation model” or “AVM” is any computerized 
model used by mortgage originators and secondary market issuers to determine the value of a 
consumer’s principal dwelling collateralizing a mortgage.  12 CFR 1026.42(i)(2)(i). 
Mortgage originators and secondary market issuers will need to consider whether the valuation 
products that they are using are (1) automated (i.e., computerized); (2) a model; and (3) 
designed to estimate the value of a consumer’s principal dwelling collateralizing a mortgage.   
2.2 Credit decisions regarding mortgages  
The final rule applies to the use of AVMs to make credit decisions regarding mortgages. 
 For purposes of the final rule, a “consumer” 
is a natural person to whom credit is offered 
or extended, even if the credit is primarily for 
business, commercial, agricultural, or 
organizational purposes.  12 CFR 
1026.2(a)(11).  Additionally, for this purpose, 
credit extended to a natural person includes 
credit extended to a trust established for tax 
or estate planning purposes and land trusts.  
See comment 2(a)(11)-3. 


 
 
7 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
2.2.1 Mortgages 
For purposes of the final rule, a mortgage includes any transaction in which a consensual 
security interest is created or retained in a consumer’s principal dwelling.  The consensual 
security interest could be a mortgage, deed of trust, 
purchase money security interest arising under an 
installment sales contract, or an equivalent consensual 
security interest.  12 CFR 1026.42(i)(2)(v).  See also 12 
CFR 1026.2(a)(11). 
Thus, for purposes of the final rule, a mortgage can be an 
open-end or closed-end transaction as long as it is 
secured by the principal dwelling of a natural person to 
whom credit is offered or extended.  Comment 42(a)-1.   
A consumer can have only one principal dwelling7 at a 
time.  Thus, a vacation or other second home would not 
be a principal dwelling.  However, if a consumer buys or 
builds a new dwelling that will become the consumer’s 
principal dwelling within a year or upon the completion 
of construction, the new dwelling is considered the 
principal dwelling for purposes of applying this definition 
to a particular transaction. Comment 2(a)(19)-4.  A 
principal dwelling does not need to be property classified 
as real property under applicable law and can include an 
individual condominium unit, cooperative unit, mobile 
home, boat, or trailer if used as a principal dwelling.  
Example 1:  Company A originates an agricultural purpose line of credit to an 
individual.  The loan is secured by farmland and a dwelling, which is the individual’s 
principal dwelling.  The loan is a mortgage for purposes of the final rule because the 
 
7  The term “dwelling” is defined in § 1026.2(a)(19).  The term “principal dwelling” has the same meaning as under 
§§ 1026.2(a)(24), 1026.15(a), and 1026.23(a).  See comments 2(a)(19)-4, 2(a)(24)-3, 15(a)(1)-5, and 23(a)-3.   
 
 A transaction can be a mortgage for purposes 
of the final rule even if the transaction is 
exempt from other provisions of Regulation 
Z.  Comment 3-2.  While the CFPB is 
codifying the final rule’s requirements in 
Regulation Z, which generally implements 
TILA, the statutory authority for this final 
rule is FIRREA. 
 As noted above, for purposes of the final rule, 
the term “consumer” does not impose any 
limits on the purpose of the transaction 
because the final rule defines “consumer” to 
mean a natural person to whom credit is 
offered or extended, even if the credit is 
primarily for business, commercial, 
agricultural, or organizational purposes.  
12  CFR 1026.2(a)(11).   A mortgage can be 
for any purpose as long as it is secured by the 
principal dwelling of a natural person to 
whom credit is offered or extended.  See 
Example 1 below. 
 


 
 
8 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
individual is a consumer for purposes of the final rule and the credit transaction creates 
a security interest in the consumer’s principal dwelling. 
Example 2:  Company A originates a business purpose loan to a corporation that has 
only one shareholder.  The shareholder is a natural person, and the loan is secured by 
the shareholder’s principal dwelling.  The loan is not a mortgage for purposes of the 
final rule because the credit was not extended to a consumer pursuant to the final rule.   
Example 3:  Company A originates a consumer purpose loan to two individuals.  The 
loan is secured by a house owned by Individual A and a boat owned by Individual B.   
The house is a vacation home and is not Individual A’s principal dwelling.  However, the 
boat is Individual B’s principal dwelling.  The loan is a mortgage for purposes of the 
final rule.  
Example 4:  Company A originates a consumer purpose loan to a trust established for 
estate planning purposes.  The loan is secured by the principal dwelling of the individual 
who established the trust.  The loan is a mortgage for purposes of the final rule because, 
pursuant to the final rule, credit extended to a trust for tax or estate planning purposes 
is considered to be credit extended to a consumer.  
2.2.2 Credit decisions 
A credit decision is a decision regarding whether and under what terms to: 
 
Originate;  
 
Modify;  
 
Terminate; or  
 
Make other changes to a mortgage. 
A credit decision includes a decision whether to extend new or additional credit or to change the 
credit limit on a line of credit.  12 CFR 1026.42(i)(2)(iv). 
As noted in the preamble, a credit decision includes decisions to make other changes to a 
mortgage beyond modifying or terminating a loan.  Such other changes would include a decision 
to approve or deny an assumption of an existing mortgage.  


 
 
9 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
Example 1:  An individual applies for a loan from Company A.  The loan will be 
secured by the individual’s principal dwelling.  Company A uses an AVM to determine 
the value of the principal dwelling, and denies the application based on that estimated 
value.  Company A has made a credit decision for purposes of the final rule.  
Example 2:  Company A has an existing line of credit account with an individual.  The 
line of credit is secured by the individual’s principal dwelling.  During the line of credit’s 
draw period, Company A uses an AVM to determine the value of the individual’s 
principal dwelling.  Based on that value, Company A decides to terminate the draw 
period.  Company A has made a credit decision for purposes of the final rule.  
Furthermore, this would be the result regardless of whether Company A extended the 
line of credit for consumer, business, or agricultural purposes.  
2.3 Covered securitization determinations 
regarding mortgage-backed securities 
The final rule applies to the use of an AVM to make a covered securitization determination 
regarding a mortgage-backed security.    
A covered securitization determination is a determination regarding: 
1. Whether to waive an appraisal requirement for a mortgage origination in connection with 
its potential sale or transfer to a secondary market issuer; or  
2. Structuring, preparing disclosures for, or marketing initial offerings of mortgage-backed 
securitizations. 
12 CFR 1026.42(i)(2)(iii). 


 
 
10 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
Example: Company A takes a mortgage application from an individual.  The 
individual’s principal dwelling will secure the mortgage loan.  Company A provides an 
estimated value of the principal dwelling to Company B, which intends to purchase the 
mortgage loan and to include it in a mortgage-backed security that Company B is 
structuring.  Company B uses an AVM to verify the estimated value provided by 
Company A.  Company B sometimes requires appraisals for properties that secure 
mortgages included in its mortgage-backed securities.  However, in this case, Company 
B waives its appraisal requirement based on the results of its AVM.   Because Company 
B will not require an appraisal to purchase the mortgage, Company A decides not to 
obtain an appraisal or to otherwise verify the value of the principal dwelling.  Company 
B, but not Company A, has made a covered securitization determination for purposes of 
the final rule.  
 
 


 
 
11 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
3.  Covered persons 
The final rule applies to persons who are mortgage originators and secondary mortgage issuers, 
as those terms are defined in the final rule.   A person can satisfy the final rule’s definition of 
mortgage originator or secondary mortgage issuer regardless of whether that person is also a 
creditor for purposes Regulation Z.  12 CFR 1026.1(c)(6).   Thus, the final rule can apply to a 
person even if that person is not a creditor pursuant to Regulation Z.  
3.1 Secondary market issuer   
For purposes of the final rule, a “secondary market issuer” is any party that creates, structures, 
or organizes a mortgage-backed securities transaction.  12 CFR 1026.42(i)(2)(vii).  As discussed 
in the final rule’s preamble, the definition of secondary market issuer includes not only the 
government sponsored enterprises (GSEs), but any other party that creates, structures, or 
organizes a mortgage-backed securities transaction. 
3.2 Mortgage originator 
For purposes of the final rule, a mortgage originator is any person8 who does any of the 
following: 
1. For direct or indirect compensation or gain or in the expectation of direct or indirect 
compensation or gain: 
a. Takes a mortgage application; 
b. Assists a consumer in obtaining or applying to obtain a mortgage; or 
c. Offers or negotiates terms of a mortgage. 
2. Represents to the public through advertising or other means of communicating or 
providing information (including the use of business cards, stationery, brochures, signs, rate 
 
8 A “person” can be a natural person or an organization, including a corporation, partnership, proprietorship, 
association, cooperative, estate, trust, or government unit.  12 CFR 1026.2(a)(22).  


 
 
12 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
lists, or other promotional items) that such person can or will provide any of the services or 
perform any of the activities described above. 
12 CFR 1026.42(i)(2)(vi)(A) and (B). 
However, the final rule excludes the following 
persons from the definition of mortgage originator: 
1. Certain persons who perform 
administrative or clerical tasks for mortgage 
originators. The definition of mortgage 
originator excludes any person who performs 
purely administrative or clerical tasks on behalf 
of a mortgage originator. 
2. Certain retailers of manufactured or 
modular homes and their employees.  The 
definition of mortgage originator excludes a 
retailer of manufactured or modular homes or 
an employee of the retailer if the retailer or 
employee, as applicable: 
a. Does not receive compensation or gain for 
engaging in activities described above that is in excess of any compensation or gain 
received in a comparable cash transaction 
b. Discloses to the consumer in writing any corporate affiliation with any creditor and, if 
the retailer has a corporate affiliation with any creditor, at least 1 unaffiliated creditor; 
and 
c. Does not directly negotiate with the consumer or lender on loan terms (including 
rates, fees, and other costs); 
3. Certain real estate brokers.  The definition of mortgage originator excludes a person or 
entity that only performs real estate brokerage activities and is licensed or registered in 
accordance with applicable State law, unless such person or entity is compensated by a 
lender, a mortgage broker, or other mortgage originator or by any agent of such lender, 
mortgage broker, or other mortgage originator; 
4. Certain seller financers.  A person that meets the criteria for seller financers provided in 
§ 1026.36(a)(4) & (5); and 
 As discussed in Section 2, a transaction can 
be a mortgage for purposes of the final rule 
even if the transaction is exempt from other 
provisions of Regulation Z.  Comment 3-2.  
For example, the scope of the final rule 
includes not only consumer purpose 
mortgages but also mortgages for business, 
commercial, agricultural, or organizational 
purposes, as long as they are secured by a 
consumer’s principal dwelling.  12 CFR 
1026.42(a); comment 42(a)-2.  Additionally, 
a “consumer” is a natural person to whom 
credit is offered or extended, even if the 
credit is primarily for business, commercial, 
agricultural, or organizational purposes.  12 
CFR 1026.2(a)(11).   


 
 
13 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
5. Servicers and servicer employees, agents, and contractors.  The definition of mortgage 
originator generally excludes servicers and their employees, agents, and contractors 
(collectively, servicing personnel).  For example, this exclusion applies when such servicers 
and servicing personnel offer or negotiate terms of a mortgage for purposes of renegotiating, 
modifying, replacing, and subordinating principal of existing mortgages where borrowers 
are behind in their payments, in default or have a reasonable likelihood of being in default or 
falling behind.  However, a person is servicer with respect to a particular transaction only 
after it is consummated, and that person retains or obtains its servicing rights.  Therefore, 
the term mortgage originator includes a servicer and its servicing personnel when they 
perform mortgage originator activities for purposes of 15 U.S.C. 1602(dd)(2) with respect to 
any transaction that constitutes a new extension of credit, including a refinancing or a 
transaction that obligates a different consumer on an existing debt.  Comment 42(i)(2)(vi)-1. 
12 CFR 1026.42(i)(2)(vi)(C) through (G). 
Example 1: Company A originates a closed-end loan to an individual.  The individual’s 
principal dwelling secures the loan.  Company A originates the mortgage using its own 
funds and then sells all rights to the mortgage to Company B.  After obtaining the rights 
to the mortgage, Company B attempts to collect scheduled periodic payments from the 
individual, but the individual becomes delinquent. Company B offers to modify the 
terms of the individual’s mortgage.  Assume the modification does not constitute a new 
extension of credit because it does not satisfy and replace the mortgage with a new 
obligation pursuant to 12 CFR 1026.20(a).  Company A is a mortgage originator for 
purposes of the final rule, but Company B is not. 
Example 2: Company A originates a closed-end loan to an individual.  The individual’s 
principal dwelling secures the loan.  Company A originates the mortgage loan using its 
own funds and then sells all rights to the mortgage loan to Company B.  After obtaining 
the rights to the mortgage loan, Company B attempts to collect scheduled periodic 
payments from the borrower, but the borrower becomes delinquent.  Company B offers 
to refinance the mortgage loan (i.e., offers a new mortgage loan secured by the 
individual’s principal dwelling that would satisfy and replace the existing mortgage 
loan).  Both Companies A and B are mortgage originators for purposes of the final rule. 
Example 3: Company A accepts an application from an individual for a business 
purpose loan that would be secured by that individual’s principal dwelling.  Company A 


 
 
14 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
is a mortgage originator for purposes of the final rule because the final rule applies to a 
business purpose loan made to a natural person if the loan would be secured by that 
natural person’s principal dwelling.   
 
 
 


 
 
15 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
4.  Quality control standards 
Mortgage originators and secondary market 
issuers that engage in credit decisions or covered 
securitization determinations must adopt and 
maintain certain policies, practices, procedures, 
and control systems regarding the AVMs they use 
when engaging in these decisions or 
determinations.  These policies, practices, procedures, and control systems must ensure that the 
AVMs used in the credit decisions and covered securitization determinations adhere to quality 
control standards designed to: 
1. Ensure a high level of confidence in the estimates produced; 
2. Protect against the manipulation of data;  
3. Seek to avoid conflicts of interest; 
4. Require random sample testing and reviews; and  
5. Comply with applicable nondiscrimination laws. 
12 CFR 1026.42(i)(3). 
This requirement applies regardless of whether the mortgage originator or secondary market 
issuer engages in credit decisions or covered securitization determinations itself or through or in 
cooperation with a third party or affiliate.  12 CFR 1026.42(i)(3). 
For purposes of the final rule, control systems are the functions (such as internal and external 
audits, risk review, quality control, and quality assurance) and information systems that are 
used to measure performance, make decisions about risk, and assess the effectiveness of 
processes and personnel, including with respect to compliance with statutes and regulations.  
12 CFR 1026.42(2)(ii). 
 
 Different policies, practices, procedures, and 
control systems may be appropriate for 
institutions of different sizes with different 
business models and risk profiles. 


 
 
16 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
Mortgage originators and secondary market 
issuers may work with AVM providers to assist 
them with their compliance obligations under the 
rule, as they do with other third-party vendors in 
order to comply with relevant regulatory 
requirements.  While mortgage originators and 
secondary market issuers should not rely solely on 
testing and validation representations provided by 
an AVM vendor, they do not necessarily need to 
conduct their own testing and validation.  They 
must, however, adopt and maintain policies, 
practices, procedures, and control systems for 
evaluating the sufficiency of the vendor’s testing 
and validation that are appropriate based on the 
size, complexity, and risk profile of the mortgage 
originator or secondary market issuer and the 
transactions for which they would use AVMs 
covered by the final rule. 
The CFPB has provided guidance on managing the risk inherent in the use of third-party service 
providers, such as outside entities that provide AVMs and AVM services.  See CFPB, Compliance 
Bulletin and Policy Guidance; 2016–02, Service Providers (Oct. 31, 2016); CFPB, Examination 
Procedures—Compliance Management Review (Aug. 2017).  In line with the CFPB’s service 
provider guidance, regardless of whether mortgage originators and secondary market issuers 
use their own AVMs or third-party AVMs, the final rule requires mortgage originators and 
secondary market issuers to adopt and maintain policies, practices, procedures, and control 
systems to ensure that those AVMs adhere to the rule’s requisite quality control standards. 
As noted in the preamble, existing nondiscrimination laws apply to appraisals and AVMs, and 
institutions have a preexisting obligation to comply with all federal laws, including federal 
nondiscrimination laws.  For example, the Equal Credit Opportunity Act and its implementing 
Regulation B bar discrimination on a prohibited basis in any aspect of a credit transaction.   
Similarly, the Fair Housing Act prohibits unlawful discrimination in all aspects of residential 
real estate-related transactions.  Policies, practices, procedures, and control systems must 
ensure that AVMs used in credit decisions and covered securitization determinations adhere to 
quality control standards designed to comply with applicable nondiscrimination laws.  
 The CFPB has published procedures for 
CFPB examiners to assess an institution’s fair 
lending related risks and controls related to 
the use of models—including, potentially, 
AVMs—in the credit decision process.  CFPB, 
ECOA Baseline Review Module 2, 6 (Apr. 
2019), available at 
https://files.consumerfinance.gov/f/docume
nts/cfpb_supervision-and-examination-
manual_ecoa-baseline-exam-
procedures_2019-04.pdf).  Mortgage 
originators and secondary market issuers 
may want to review these procedures for 
additional information regarding risks and 
controls to ensure AVMs comply with federal 
nondiscrimination laws.  


 
 
17 
SMALL ENTITY COMPLIANCE GUIDE:  AUTOMATED VALUATIONS RULE 
VERSION 1.0 
5.  Effective date 
The final rule is effective on October 1, 2025.  Mortgage originators and secondary market 
issuers must begin complying with the final rule on that date.  
