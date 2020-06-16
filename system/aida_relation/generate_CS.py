import argparse
import os

rel_map_ACE = {u'PART-WHOLE_Artifact(Arg-1,Arg-2)': 28, u'ORG-AFF_Investor-Shareholder(Arg-1,Arg-2)': 12,
               u'ORG-AFF_Sports-Affiliation(Arg-1,Arg-2)': 21,
               u'ORG-AFF_Membership(Arg-1,Arg-2)': 18, u'ORG-AFF_Employment(Arg-2,Arg-1)': 8,
               u'ART_User-Owner-Inventor-Manufacturer(Arg-2,Arg-1)': 14,
               u'ORG-AFF_Investor-Shareholder(Arg-2,Arg-1)': 9, u'PER-SOC_Business(Arg-1,Arg-1)': 23,
               u'GEN-AFF_Org-Location(Arg-2,Arg-1)': 5,
               u'PART-WHOLE_Subsidiary(Arg-2,Arg-1)': 4, u'ORG-AFF_Founder(Arg-2,Arg-1)': 27,
               u'PART-WHOLE_Artifact(Arg-2,Arg-1)': 31, u'ORG-AFF_Membership(Arg-2,Arg-1)': 24,
               u'ART_User-Owner-Inventor-Manufacturer(Arg-1,Arg-2)': 13, u'PHYS_Near(Arg-1,Arg-1)': 16,
               u'GEN-AFF_Citizen-Resident-Religion-Ethnicity(Arg-1,Arg-2)': 17,
               u'PART-WHOLE_Subsidiary(Arg-1,Arg-2)': 11, u'PER-SOC_Lasting-Personal(Arg-1,Arg-1)': 20,
               u'PART-WHOLE_Geographical(Arg-1,Arg-2)': 0,
               u'GEN-AFF_Org-Location(Arg-1,Arg-2)': 6, u'ORG-AFF_Founder(Arg-1,Arg-2)': 25,
               u'ORG-AFF_Student-Alum(Arg-1,Arg-2)': 22,
               u'GEN-AFF_Citizen-Resident-Religion-Ethnicity(Arg-2,Arg-1)': 7, u'ORG-AFF_Ownership(Arg-2,Arg-1)': 30,
               u'ORG-AFF_Ownership(Arg-1,Arg-2)': 29,
               u'ORG-AFF_Employment(Arg-1,Arg-2)': 10, u'PER-SOC_Family(Arg-1,Arg-1)': 15,
               u'ORG-AFF_Student-Alum(Arg-2,Arg-1)': 19, u'NO-RELATION(Arg-1,Arg-1)': 1,
               u'ORG-AFF_Sports-Affiliation(Arg-2,Arg-1)': 26, u'PHYS_Located(Arg-1,Arg-1)': 2,
               u'PART-WHOLE_Geographical(Arg-2,Arg-1)': 3}

rel_map_ERE = {'physical_locatednear(Arg-1,Arg-2)': 0,
               'physical_locatednear(Arg-2,Arg-1)': 1,
               'physical_resident(Arg-1,Arg-2)': 2,
               'physical_resident(Arg-2,Arg-1)': 3,
               'physical_orgheadquarter(Arg-1,Arg-2)': 4,
               'physical_orgheadquarter(Arg-2,Arg-1)': 5,
               'physical_orglocationorigin(Arg-1,Arg-2)': 6,
               'physical_orglocationorigin(Arg-2,Arg-1)': 7,
               'partwhole_subsidiary(Arg-1,Arg-2)': 8,
               'partwhole_subsidiary(Arg-2,Arg-1)': 9,
               'partwhole_membership(Arg-1,Arg-2)': 10,
               'partwhole_membership(Arg-2,Arg-1)': 11,
               'personalsocial_business(Arg-1,Arg-2)': 12,
               'personalsocial_business(Arg-2,Arg-1)': 12,
               'personalsocial_family(Arg-1,Arg-2)': 13,
               'personalsocial_family(Arg-2,Arg-1)': 13,
               'personalsocial_unspecified(Arg-1,Arg-2)': 14,
               'personalsocial_unspecified(Arg-2,Arg-1)': 14,
               'personalsocial_role(Arg-1,Arg-2)': 15,
               'personalsocial_role(Arg-2,Arg-1)': 15,
               'orgaffiliation_employmentmembership(Arg-1,Arg-2)': 16,
               'orgaffiliation_employmentmembership(Arg-2,Arg-1)': 17,
               'orgaffiliation_leadership(Arg-1,Arg-2)': 18,
               'orgaffiliation_leadership(Arg-2,Arg-1)': 19,
               'orgaffiliation_investorshareholder(Arg-1,Arg-2)': 20,
               'orgaffiliation_investorshareholder(Arg-2,Arg-1)': 21,
               'orgaffiliation_studentalum(Arg-1,Arg-2)': 22,
               'orgaffiliation_studentalum(Arg-2,Arg-1)': 23,
               'orgaffiliation_ownership(Arg-1,Arg-2)': 24,
               'orgaffiliation_ownership(Arg-2,Arg-1)': 25,
               'orgaffiliation_founder(Arg-1,Arg-2)': 26,
               'orgaffiliation_founder(Arg-2,Arg-1)': 27,
               'generalaffiliation_more(Arg-1,Arg-2)': 28,
               'generalaffiliation_more(Arg-2,Arg-1)': 29,
               'generalaffiliation_opra(Arg-1,Arg-2)': 30,
               'generalaffiliation_opra(Arg-2,Arg-1)': 31,
               'NO-RELATION(Arg-1,Arg-1)': 32,
               'generalaffiliation_personage(Arg-1,Arg-2)': 32,
               'generalaffiliation_personage(Arg-2,Arg-1)': 32,
               'generalaffiliation_orgwebsite(Arg-1,Arg-2)': 32,
               'generalaffiliation_orgwebsite(Arg-2,Arg-1)': 32,
               'generalaffiliation_apora(Arg-1,Arg-2)': 33,
               'generalaffiliation_apora(Arg-2,Arg-1)': 34,
               'sponsorship(Arg-1,Arg-2)': 35
               }
single_ERE = {'personalsocial_business(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Business',
              'personalsocial_business(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Business',
              'personalsocial_family(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Family',
              'personalsocial_family(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Family',
              'personalsocial_unspecified(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Unspecified',
              'personalsocial_unspecified(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Unspecified',
              'personalsocial_role(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.RoleTitle',
              'personalsocial_role(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.RoleTitle'
              }
ACE_to_AIDA_ouput = {u'PHYS_Near(Arg-1,Arg-1)': u'Physical.Located-Near',
                     u'PHYS_Located(Arg-1,Arg-1)': u'Physical.Located-Near',
                     u'GEN-AFF_Org-Location(Arg-1,Arg-2)': u'Physical.Organization-Location-Origin',
                     u'GEN-AFF_Org-Location(Arg-2,Arg-1)': u'Physical.Organization-Location-Origin',
                     u'PART-WHOLE_Subsidiary(Arg-1,Arg-2)': u'Part-Whole.Subsidiary',
                     u'PART-WHOLE_Subsidiary(Arg-2,Arg-1)': u'Part-Whole.Subsidiary',
                     u'ORG-AFF_Membership(Arg-1,Arg-2)': u'Part-Whole.Membership',
                     u'ORG-AFF_Membership(Arg-2,Arg-1)': u'Part-Whole.Membership',
                     u'PER-SOC_Business(Arg-1,Arg-1)': u'Personal-Social.Business',
                     u'PER-SOC_Family(Arg-1,Arg-1)': u'Personal-Social.Business',
                     u'ORG-AFF_Employment(Arg-1,Arg-2)': u'OrganizationAffiliation.EmploymentMembership',
                     u'ORG-AFF_Employment(Arg-2,Arg-1)': u'OrganizationAffiliation.EmploymentMembership',
                     u'ORG-AFF_Investor-Shareholder(Arg-1,Arg-2)': u'Organization-Affiliation.Investor-Shareholder',
                     u'ORG-AFF_Investor-Shareholder(Arg-2,Arg-1)': u'Organization-Affiliation.Investor-Shareholder',
                     u'ORG-AFF_Student-Alum(Arg-1,Arg-2)': u'orgafl.Organization-Affiliation.Student-Alum',
                     u'ORG-AFF_Student-Alum(Arg-2,Arg-1)': u'orgafl.Organization-Affiliation.Student-Alum',
                     u'ORG-AFF_Ownership(Arg-1,Arg-2)': u'Organization-Affiliation.Ownership',
                     u'ORG-AFF_Ownership(Arg-2,Arg-1)': u'Organization-Affiliation.Ownership',
                     u'ORG-AFF_Founder(Arg-1,Arg-2)': u'OrganizationAffiliation.Founder',
                     u'ORG-AFF_Founder(Arg-2,Arg-1)': u'OrganizationAffiliation.Founder',
                     u'GEN-AFF_Citizen-Resident-Religion-Ethnicity(Arg-1,Arg-2)': u'General-Affiliation.Person-Member-Origin-Religion-Ethnicity (MORE)',
                     u'GEN-AFF_Citizen-Resident-Religion-Ethnicity(Arg-2,Arg-1)': u'General-Affiliation.Person-Member-Origin-Religion-Ethnicity (MORE)'
                     }

ACE_to_AIDA_final_output = {
    u'PHYS_Near(Arg-1,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.LocatedNear',
    u'PHYS_Located(Arg-1,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.LocatedNear',
    u'GEN-AFF_Org-Location(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.OrganizationLocationOrigin',
    u'GEN-AFF_Org-Location(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.OrganizationLocationOrigin',
    u'PART-WHOLE_Subsidiary(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Subsidiary',
    u'PART-WHOLE_Subsidiary(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Subsidiary',
    u'ORG-AFF_Membership(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Membership',
    u'ORG-AFF_Membership(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Membership',
    u'PER-SOC_Business(Arg-1,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Business',
    u'PER-SOC_Family(Arg-1,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Business',
    u'ORG-AFF_Employment(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.EmploymentMembership',
    u'ORG-AFF_Employment(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.EmploymentMembership',
    u'ORG-AFF_Investor-Shareholder(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.InvestorShareholder',
    u'ORG-AFF_Investor-Shareholder(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.InvestorShareholder',
    u'ORG-AFF_Student-Alum(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.StudentAlum',
    u'ORG-AFF_Student-Alum(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.StudentAlum',
    u'ORG-AFF_Ownership(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Ownership',
    u'ORG-AFF_Ownership(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Ownership',
    u'ORG-AFF_Founder(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Founder',
    u'ORG-AFF_Founder(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Founder',
    u'GEN-AFF_Citizen-Resident-Religion-Ethnicity(Arg-1,Arg-2)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.MORE',
    u'GEN-AFF_Citizen-Resident-Religion-Ethnicity(Arg-2,Arg-1)': u'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.MORE'
}

ERE_to_AIDA_final_ouput = {
    'physical_locatednear(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.LocatedNear',
    'physical_locatednear(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.LocatedNear',
    'physical_resident(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.Resident',
    'physical_resident(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.Resident',
    'physical_orgheadquarter(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.OrganizationHeadquarter',
    'physical_orgheadquarter(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.OrganizationHeadquarter',
    'physical_orglocationorigin(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.OrganizationLocationOrigin',
    'physical_orglocationorigin(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Physical.OrganizationLocationOrigin',
    'partwhole_subsidiary(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Subsidiary',
    'partwhole_subsidiary(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Subsidiary',
    'partwhole_membership(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Membership',
    'partwhole_membership(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PartWhole.Membership',
    'personalsocial_business(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Business',
    'personalsocial_business(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Business',
    'personalsocial_family(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Family',
    'personalsocial_family(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Family',
    'personalsocial_unspecified(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Unspecified',
    'personalsocial_unspecified(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.Unspecified',
    'personalsocial_role(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.RoleTitle',
    'personalsocial_role(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#PersonalSocial.RoleTitle',
    'orgaffiliation_employmentmembership(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.EmploymentMembership',
    'orgaffiliation_employmentmembership(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.EmploymentMembership',
    'orgaffiliation_leadership(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Leadership',
    'orgaffiliation_leadership(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Leadership',
    'orgaffiliation_investorshareholder(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.InvestorShareholder',
    'orgaffiliation_investorshareholder(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.InvestorShareholder',
    'orgaffiliation_studentalum(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.StudentAlum',
    'orgaffiliation_studentalum(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.StudentAlum',
    'orgaffiliation_ownership(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Ownership',
    'orgaffiliation_ownership(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Ownership',
    'orgaffiliation_founder(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Founder',
    'orgaffiliation_founder(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#OrganizationAffiliation.Founder',
    'generalaffiliation_more(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.MORE',
    'generalaffiliation_more(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.MORE',
    'generalaffiliation_opra(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.OPRA',
    'generalaffiliation_opra(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.OPRA',
    'NO-RELATION(Arg-1,Arg-1)': 'NO-RELATION(Arg-1,Arg-1)',
    'generalaffiliation_personage(Arg-1,Arg-2)': 'NO-RELATION(Arg-1,Arg-1)',
    'generalaffiliation_personage(Arg-2,Arg-1)': 'NO-RELATION(Arg-1,Arg-1)',
    'generalaffiliation_orgwebsite(Arg-1,Arg-2)': 'NO-RELATION(Arg-1,Arg-1)',
    'generalaffiliation_orgwebsite(Arg-2,Arg-1)': 'NO-RELATION(Arg-1,Arg-1)',
    'generalaffiliation_apora(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.APORA',
    'generalaffiliation_apora(Arg-2,Arg-1)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.APORA',
    'sponsorship(Arg-1,Arg-2)': 'https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GeneralAffiliation.Sponsorship'
}


def generate_cs_file(edl_cs_string, rel_map_ERE, ERE_to_AIDA_final_ouput,
                     plain_text="temp/AIDA_plain_text.txt", final_results="temp/results_post_sponsor.txt"):
    id_relation = {}
    for key in rel_map_ERE:
        id_relation[str(rel_map_ERE[key])] = key
    results = []
    score = []
    with open(final_results) as fmodel:
        for line in fmodel:
            results.append(id_relation[line.strip().split("\t")[0]])
            score.append(line.strip().split("\t")[1][:4])

    mention1 = []
    mention2 = []
    output = []
    i = 0

    score_idx = 0
    query_id = 0
###########################
# mention ID to KB ID
###########################
    mid2kbid = {}
    test = 0
    for one_line in edl_cs_string.split("\n")[2:]:
        temp = one_line.strip().split("\t")
        if "mention" in temp[1]:
            test += 1
            mid2kbid[temp[3].strip()] = temp[0].strip()
    error = 0
    with open(plain_text) as fmodel:
        for line in fmodel:
            temp = line.strip().split("\t")
            fixed_temp = temp[2].strip().split(":")
            mention1 = fixed_temp[0] + ":" + fixed_temp[1].split(" ",1)[0]
            mention2 = fixed_temp[1].split(" ",1)[1] + ":" + fixed_temp[2]
            type1 = temp[1].strip().split(" ")[0].strip()
            type2 = temp[1].strip().split(" ")[1].strip()
            seg_offset = temp[3].strip()
            try:
                var1 = mid2kbid[mention1]
                var2 = mid2kbid[mention2]
            except:
                continue
            if ERE_to_AIDA_final_ouput[results[i]] != 'NO-RELATION(Arg-1,Arg-1)' and mid2kbid[mention1] != mid2kbid[mention2]:
                query_id += 1
                relation_format = results[i].split("(")[0]
                relation_arg = results[i].split("(")[1].strip().split(",")[0]
                if relation_arg == "Arg-1":
                    if results[i] in ERE_to_AIDA_final_ouput:
                        try:
                            output.append(mid2kbid[mention1] + "\t" + ERE_to_AIDA_final_ouput[results[i]] + "\t" + mid2kbid[
                                mention2] + "\t" + seg_offset + "\t" + score[score_idx])# + "\n")
                        except:
                            error += 1
                else:
                    if results[i] in ERE_to_AIDA_final_ouput and results[i] not in single_ERE:
                        try:
                            output.append(mid2kbid[mention2] + "\t" + ERE_to_AIDA_final_ouput[results[i]] + "\t" + mid2kbid[
                                mention1] + "\t" + seg_offset + "\t" + score[score_idx])# + "\n")
                        except:
                            error += 1
                    elif results[i] in ERE_to_AIDA_final_ouput and results[i] in single_ERE:
                        try:
                            output.append(mid2kbid[mention1] + "\t" + ERE_to_AIDA_final_ouput[results[i]] + "\t" + mid2kbid[
                                mention2] + "\t" + seg_offset + "\t" + score[score_idx])# + "\n")
                        except:
                            error += 1
                    else:
                        pass
            i += 1
            score_idx += 1
    print(error)
    # output.append('\n')
    return output