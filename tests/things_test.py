import datetime
from aecore.test_utils import BaseTestCase
from google.appengine.ext.ndb.query import OR
from aecore import types


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class TestPerson(BaseTestCase):

    def setUp(self):
        super(TestPerson, self).setUp()
        self.register_model('Person', types.Person)

    def test_create(self):
        # Create a Provider Profile Model
        et = types
        person = et.Person()
        person.givenName = u'Joseph'
        person.additionalName = u'Robert'
        person.familyName = u'Smarr'
        person.honorificPrefix = u'Mr.'
        person.honorificSuffix = u'Esq.'
        name_formatted = u'Mr. Joseph Robert Smarr, Esq.'
        person.provider = u'google'
        person.id = u'12345'
        #        person.display_name = u'Mr. Joseph Robert Smarr, Esq.'
        #        person.nickname = u'The Smarr'
        person.image = u'http://awesome.jpg.to/'
        person.birthDate = datetime.datetime.now() - datetime.timedelta(365*30)
        person.gender = u'male'
        #        person.note = u'Note about this person form the provider.\n With line breaks.'
        person.description = u'This is the description section \n With line breaks.'
        person.telephone = u'555-333-4445'
        #        person.tagline = u'No problem can be solved from the same level of consciousness that created it.'
        person.utcOffset = u'-6'
        person.languagesSpoken = [et.Language(name=u'english', proficiency=5), et.Language(name=u'esperanto', proficiency=1)]
        person.location = et.Place(name=u'Springfield, VT ')
        person.relationshipStatus = u'single'
        person.dateCreated = datetime.datetime.now() - datetime.timedelta(365*3)
        person.dateModified = datetime.datetime.now() - datetime.timedelta(1)
        person.locale = u'en-us'
        person.verified = True

        child1 = et.Person()
        child1.givenName = u'Billy'
        child1.additionalName = u'Joe'
        child1.familyName = u'Smarr'
        person.children = [child1]

        parent1 = et.Person()
        parent1.givenName = u'Bob'
        parent1.additionalName = u'Joe'
        parent1.familyName = u'Smarr'
        person.parent = [parent1]

        usa = et.Country()
        usa.name = u'USA'
        # Create an Address Model
        address1 = et.PostalAddress()
        address1.description = u'work'
        address1.addressCountry = usa
        address1.addressLocality = u'Springfield'
        address1.addressRegion = u'VT'
        address1.postalCode = u'12345'
        address1.streetAddress = u'742 Evergreen Terrace\nSuite 123'
        address1_formatted = u'742 Evergreen Terrace\nSuite 123\nSpringfield, VT 12345 USA'

        person.address = address1

        address2 = et.PostalAddress()
        address2.description = u'home'
        address2.addressLocality = u'Springfield'
        address2.addressRegion = u'VT'
        address2.country = usa
        address2_formatted = u'Springfield, VT USA'

        org1 = et.Organization()
        org1.name = u'Scotch Media, LLC.'
        org1.description = u'Creative, Design, Development'
        org1.address = address2
        org1.location = et.Place(name=u'Kansas USA')

        org2 = et.Organization()
        org2.name = u'FHSU'
        org2.description = u'Fort Hays State University'
        org2.address = et.PostalAddress(addressLocality=u'Hays',
            addressRegion=u'Kansas', addressCountry=et.Country(name=u'USA'))
        org2.location = et.Place(name=u'Kansas USA')

        person.worksFor = org1
        affiliation1 = et.Affiliation()
        affiliation1.organization = org1
        affiliation1.department = u'Creative'
        affiliation1.name = u'CCO'
        affiliation1.description = u'Chief Creative Officer'
        affiliation1.startDate = datetime.datetime.now() - datetime.timedelta(400)
        affiliation1.endDate = datetime.datetime.now() - datetime.timedelta(300)
        affiliation1.location = et.Place(name=u'Kansas USA')
        affiliation2 = et.Affiliation()
        affiliation2.organization = org2
        affiliation2.department = u'Graphic Design'
        affiliation2.name = u'BFA'
        affiliation2.description = u'BFA Emphasis in Graphic Design'
        affiliation2.startDate = datetime.datetime.now() - datetime.timedelta(400)
        affiliation2.endDate = datetime.datetime.now() - datetime.timedelta(300)
        affiliation2.location = et.Place(name=u'Hays, KS USA')
        person.affiliations  = [affiliation1, affiliation2]

        skill1 = et.Skill()
        skill1.name = u'python'
        skill1.years = 2
        skill1.proficiency = 3
        person.skills = [skill1]

        certification = et.Certification()
        certification.name = u'Dr. license'
        certification.authority = et.Organization(name=u'Texas Board of Medicine')
        certification.startDate = datetime.datetime.now() - datetime.timedelta(365*5)
        certification.startDate = datetime.datetime.now() + datetime.timedelta(365*1)
        certification.value = u'12345'
        person.certifications = [certification]

        account1 = et.Account()
        account1.name = u'twitter'
        account1.url = u'twitter.com'
        account1.username = u'scotchmedia'

        account2 = et.Account()
        account2.name = u'facebook'
        account2.url = u'facebook.com'
        account2.userid = u'12345'
        person.accounts = [account1, account2]

        email1 = et.Email()
        email1.address = u'example1@example.com'
        email1.description = u'home'
        email1.primary = False
        email1.verified = True
        email2 = et.Email()
        email2.address = u'example2@example.com'
        email2.description = u'work'
        email2.primary = True
        email2.verified = False
        person.emails = [email1, email2]

        im1 = et.IM()
        im1.address = u'im1@example.com'
        im1.description = u'aim'
        im1.primary = False
        im1.verified = True
        im2 = et.IM()
        im2.address = u'im2@example.com'
        im2.description = u'gtalk'
        im2.primary = True
        im2.verified = False
        person.ims = [im1, im2]

        url1 = et.URL()
        url1.url = u'example.com'
        url1.description = u'home'
        url1.primary = False
        url1.verified = True
        url2 = et.URL()
        url2.url = u'blog.example.org'
        url2.description = u'blog'
        url2.primary = True
        url2.verified = False
        person.urls = [url1, url2]
        # Save
        saved = person.put()
        # retrieve from datastore
        qry1 = et.Person.query().get()

        self.assertEqual(qry1.provider, person.provider)
        self.assertEqual(qry1.id, person.id)
        self.assertEqual(qry1.image, person.image)
        self.assertEqual(qry1.givenName, person.givenName)
        self.assertEqual(qry1.familyName, person.familyName)
        self.assertEqual(qry1.additionalName, person.additionalName)
        self.assertEqual(qry1.honorificPrefix, person.honorificPrefix)
        self.assertEqual(qry1.honorificSuffix, person.honorificSuffix)

        self.assertEqual(qry1.children[0].givenName, child1.givenName)
        self.assertEqual(qry1.children[0].familyName, child1.familyName)
        self.assertEqual(qry1.children[0].additionalName, child1.additionalName)

        self.assertEqual(qry1.provider, person.provider)
        self.assertEqual(qry1.id, person.id)
        #        self.assertEqual(qry1.nickname, person.nickname)
        self.assertEqual(qry1.birthDate, person.birthDate)
        self.assertEqual(qry1.description, person.description)
        self.assertEqual(qry1.telephone, person.telephone)
        #        self.assertEqual(qry1.tagline, person.tagline)
        self.assertEqual(qry1.utcOffset, person.utcOffset)
        self.assertEqual(qry1.dateModified, person.dateModified)
        self.assertEqual(qry1.dateCreated, person.dateCreated)

        self.assertEqual(qry1.location, person.location)
        self.assertEqual(qry1.relationshipStatus, person.relationshipStatus)
        self.assertEqual(qry1.locale, person.locale)
        self.assertEqual(qry1.verified, person.verified)

        # Address
        self.assertEqual(qry1.address.streetAddress, address1.streetAddress)
        self.assertEqual(qry1.address.addressLocality, address1.addressLocality)
        self.assertEqual(qry1.address.addressRegion, address1.addressRegion)
        self.assertEqual(qry1.address.postalCode, address1.postalCode)
        self.assertEqual(qry1.address.addressCountry, usa)
        self.assertEqual(qry1.address.description, address1.description)

        # Organizations
        self.assertEqual(qry1.worksFor.name, org1.name)
        self.assertEqual(qry1.worksFor.description, org1.description)
        self.assertEqual(qry1.worksFor.address, org1.address)
        self.assertEqual(qry1.worksFor.location, org1.location)

        # Affiliation
        self.assertEqual(qry1.affiliations[0].startDate, affiliation1.startDate)
        self.assertEqual(qry1.affiliations[0].endDate, affiliation1.endDate)
        self.assertEqual(qry1.affiliations[0].location, affiliation1.location)
        self.assertEqual(qry1.affiliations[0].name, affiliation1.name)
        self.assertEqual(qry1.affiliations[0].department, affiliation1.department)
        self.assertEqual(qry1.affiliations[0].description, affiliation1.description)
        #        self.assertEqual(qry1.affiliations[0].organization, affiliation1.organization)
        self.assertEqual(qry1.affiliations[0], affiliation1)
        self.assertEqual(qry1.affiliations[1].startDate, affiliation2.startDate)
        self.assertEqual(qry1.affiliations[1].endDate, affiliation2.endDate)
        self.assertEqual(qry1.affiliations[1].location, affiliation2.location)
        self.assertEqual(qry1.affiliations[1].name, affiliation2.name)
        self.assertEqual(qry1.affiliations[1].department, affiliation2.department)
        self.assertEqual(qry1.affiliations[1].description, affiliation2.description)
        #        self.assertEqual(qry1.affiliations[1].organization, affiliation2.organization)
        self.assertEqual(qry1.affiliations[1], affiliation2)

        # languagesSpoken
        self.assertEqual(qry1.languagesSpoken[0].name, person.languagesSpoken[0].name)
        self.assertEqual(qry1.languagesSpoken[0].proficiency, person.languagesSpoken[0].proficiency)

        # Skills
        self.assertEqual(qry1.skills[0].name, person.skills[0].name)
        self.assertEqual(qry1.skills[0].proficiency, person.skills[0].proficiency)
        self.assertEqual(qry1.skills[0].years, person.skills[0].years)

        # Certifications
        self.assertEqual(qry1.certifications[0].name, person.certifications[0].name)
        self.assertEqual(qry1.certifications[0].value, person.certifications[0].value)
        self.assertEqual(qry1.certifications[0].authority, person.certifications[0].authority)
        self.assertEqual(qry1.certifications[0].authority.name, person.certifications[0].authority.name)
        self.assertEqual(qry1.certifications[0].startDate, person.certifications[0].startDate)
        self.assertEqual(qry1.certifications[0].endDate, person.certifications[0].endDate)


        # Accounts
        self.assertEqual(qry1.accounts[0].url, account1.url)
        self.assertEqual(qry1.accounts[0].username, account1.username)
        self.assertEqual(qry1.accounts[1].url, account2.url)
        self.assertEqual(qry1.accounts[1].userid, account2.userid)

        # Emails
        self.assertEqual(qry1.emails[0].description,   email1.description)
        self.assertEqual(qry1.emails[0].address,       email1.address)
        self.assertEqual(qry1.emails[0].name,          email1.name)
        self.assertEqual(qry1.emails[0].primary,       email1.primary)
        self.assertEqual(qry1.emails[0].verified,      email1.verified)
        self.assertEqual(qry1.emails[1].description,   email2.description)
        self.assertEqual(qry1.emails[1].address,       email2.address)
        self.assertEqual(qry1.emails[1].name,          email2.name)
        self.assertEqual(qry1.emails[1].primary,       email2.primary)
        self.assertEqual(qry1.emails[1].verified,      email2.verified)

        # IMs
        self.assertEqual(qry1.ims[0].description,   im1.description)
        self.assertEqual(qry1.ims[0].address,       im1.address)
        self.assertEqual(qry1.ims[0].name,          im1.name)
        self.assertEqual(qry1.ims[0].primary,       im1.primary)
        self.assertEqual(qry1.ims[0].verified,      im1.verified)
        self.assertEqual(qry1.ims[1].description,   im2.description)
        self.assertEqual(qry1.ims[1].address,       im2.address)
        self.assertEqual(qry1.ims[1].name,          im2.name)
        self.assertEqual(qry1.ims[1].primary,       im2.primary)
        self.assertEqual(qry1.ims[1].verified,      im2.verified)

        # URLs
        self.assertEqual(qry1.urls[0].description,   url1.description)
        self.assertEqual(qry1.urls[0].url,           url1.url)
        self.assertEqual(qry1.urls[0].name,          url1.name)
        self.assertEqual(qry1.urls[0].primary,       url1.primary)
        self.assertEqual(qry1.urls[0].verified,      url1.verified)
        self.assertEqual(qry1.urls[1].description,   url2.description)
        self.assertEqual(qry1.urls[1].url,           url2.url)
        self.assertEqual(qry1.urls[1].name,          url2.name)
        self.assertEqual(qry1.urls[1].primary,       url2.primary)
        self.assertEqual(qry1.urls[1].verified,      url2.verified)

        # Test Queries
        name = u'Billy'
        qry2 = et.Person.query(
            OR(
                et.Person.givenName == name,
                et.Person.parents.givenName == name,
                et.Person.children.givenName == name
            )
        ).get()

        self.assertTrue(qry2 is not None)

        q_email = u'example1@example.com'
        q1_r = et.Person.query(et.Person.emails.address == q_email).get()
        self.assertTrue(q1_r is not None)
        q_email = u'face@example.com'
        q1_r = et.Person.query(et.Person.emails.address == q_email).get()

        self.assertTrue(q1_r is None)

        m_dict = qry1.to_dict()


class TestPersonMerge(BaseTestCase):

    def setUp(self):
        super(TestPersonMerge, self).setUp()
        self.register_model('Person', types.Person)

    def test_profile_to_profile(self):
        from aecore.models import profile_merge
        # Create a Provider Profile Model
        et = types
        person = et.Person()
        person.givenName = u'Joseph'
        person.additionalName = u'Robert'
        person.familyName = u'Smarr'
        person.honorificPrefix = u'Mr.'
        person.honorificSuffix = u'Esq.'
        name_formatted = u'Mr. Joseph Robert Smarr, Esq.'
        person.provider = u'google'
        person.id = u'12345'
        person.image = u'http://awesome.jpg.to/'
        person.birthDate = datetime.datetime.now() - datetime.timedelta(365*30)
        person.gender = u'male'
        person.description = u'This is the description section \n With line breaks.'
        person.telephone = u'555-333-4445'
        person.utcOffset = u'-6'
        person.languagesSpoken = [et.Language(name=u'english', proficiency=5), et.Language(name=u'esperanto', proficiency=1)]
        person.location = et.Place(name=u'Springfield, VT ')
        person.relationshipStatus = u'single'
        person.dateCreated = datetime.datetime.now() - datetime.timedelta(365*3)
        person.dateModified = datetime.datetime.now() - datetime.timedelta(1)
        person.locale = u'en-us'
        person.verified = True

        account1 = et.Account()
        account1.name = u'twitter'
        account1.url = u'twitter.com'
        account1.username = u'scotchmedia'

        account2 = et.Account()
        account2.name = u'facebook'
        account2.url = u'facebook.com'
        account2.userid = u'12345'

        person.accounts = [account1, account2]

        p_1 = person
        p_2 = types.Person()
        p_2.familyName = u"NewFamilyName"
        p_2.givenName = u"NewGivenName"

        account3 = types.Account()
        account3.name = u"existing"
        account3.url = u"existing.com"
        p_2.accounts = [account3]

        p_3 = profile_merge(p_2.to_dict(), p_1.to_dict())

        # existing attributes
        self.assertEqual(p_3['familyName'], u"NewFamilyName")
        self.assertEqual(p_3['givenName'], u"NewGivenName")

        # new attributes
        self.assertEqual(p_3['additionalName'], u"Robert")

        # combined attributes
        self.assertEqual(len(p_3['accounts']), 3)

        # These value should not replace existing ones.
        p_4 = types.Person()
        p_4.familyName = u"ChangedFamilyName"
        p_4.givenName = u"ChangedGivenName"

        account3 = types.Account()
        account3.name = u"existing"
        account3.url = u"changed.com"
        p_4.accounts = [account3]

        p_5 = profile_merge(p_3, p_4.to_dict())

        # Should remain the same
        self.assertEqual(p_5['familyName'], u"NewFamilyName")
        self.assertEqual(p_5['givenName'], u"NewGivenName")

        # new attributes
        self.assertEqual(p_5['additionalName'], u"Robert")

        # combined attributes
        self.assertEqual(len(p_5['accounts']), 3)
        self.assertEqual(p_5['accounts'][0]['name'], 'existing')
        self.assertEqual(p_5['accounts'][0]['url'], 'existing.com')

#    @classmethod
#    def from_dict(cls, obj_dict):
#        obj = cls()
#        for name, value in obj_dict.items():
#            prop = getattr(cls, name)  # Raises AttributeError for unknown properties.
#            if not isinstance(prop, ndb.Property):
#                raise TypeError('Cannot set non-property %s' % name)
#            if isinstance(prop, ndb.StructuredProperty) or \
#            isinstance(prop, ndb.LocalStructuredProperty):
#                if isinstance(value, list) or value is None:
#                    pass
#                else:
#                    value = prop._modelclass(**value)
#            prop._set_value(obj, value)
#        return obj
