
__author__ = 'kyle.finley@gmail.com (Kyle Finley)'

from google.appengine.ext import ndb


__all__ = [
    'Thing',
        'CreativeWork',
        'Event',
            'UserInteraction',
        'Organization',
            'EducationalOrganization',
        'Intangible',
            'PersonalAttribute',
                'Language',
                'Skill',
                'Certification',
            'Account',
            'Email',
            'IM',
            'URL',
            'Affiliation',
            'Rating',
                'AggregateRating',
            'Offer',
            'StructuredValue',
                'ContactPoint',
                'PostalAddress',
        'Place',
            'AdministrativeArea',
            'City',
            'Country',
            'State',
        'Person',
        'Product',
]


class Thing(ndb.Model):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Thing')
    description = ndb.StringProperty()
    image = ndb.StringProperty()
    name = ndb.StringProperty()
    url = ndb.StringProperty()

class Place(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Place')

class Event(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Event')
    # Todo change to date offset
    duration = ndb.DateTimeProperty()
    endDate = ndb.DateTimeProperty()
    location = ndb.StructuredProperty(Place)
    startDate = ndb.DateTimeProperty()

class UserInteraction(Event):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserInteraction')

class UserBlocks(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserBlocks')

class UserCheckins(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserCheckins')

class UserComments(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserComments')

class UserDownloads(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserDownloads')

class UserLikes(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserLikes')

class UserPageVisits(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserPageVisits')

class UserPlays(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserPlays')

class UserPlusOnes(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserPlusOnes')

class UserTweets(UserInteraction):
    itemtype = ndb.StringProperty(default=u'http://schema.org/UserTweets')

class AdministrativeArea(Place):
    itemtype = ndb.StringProperty(default=u'http://schema.org/AdministrativeArea')

class City(AdministrativeArea):
    itemtype = ndb.StringProperty(default=u'http://schema.org/City')

class Country(AdministrativeArea):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Country')

class State(AdministrativeArea):
    itemtype = ndb.StringProperty(default=u'http://schema.org/State')

class Intangible(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Intangible')

class Account(Intangible):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Account')
    username = ndb.StringProperty()
    userid = ndb.StringProperty()


class OnlineService():
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Email')
    value = ndb.StringProperty()
    verified = ndb.BooleanProperty()
    primary = ndb.StringProperty()


class Email(Intangible):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Email')
    address = ndb.StringProperty()
    verified = ndb.BooleanProperty()
    primary = ndb.BooleanProperty()

class IM(Intangible):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/IM')
    address = ndb.StringProperty()
    verified = ndb.BooleanProperty()
    primary = ndb.BooleanProperty()

class URL(Intangible):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/URL')
    primary = ndb.BooleanProperty()
    verified = ndb.BooleanProperty()

class PersonalAttribute(Intangible):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/PersonalAttribute')

class Skill(PersonalAttribute):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Skill')
    years = ndb.IntegerProperty()
    proficiency = ndb.IntegerProperty(default=0)

class Language(PersonalAttribute):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Language')
    proficiency = ndb.IntegerProperty(default=0)

class Rating(Intangible):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Rating')
    bestRating = ndb.IntegerProperty(default=5)
    ratingValue = ndb.StringProperty()
    worstRating = ndb.IntegerProperty(default=1)

class AggregateRating(Rating):
    itemtype = ndb.StringProperty(default=u'http://schema.org/AggregateRating')
    itemReviewed = ndb.StructuredProperty(Thing)
    ratingCount = ndb.IntegerProperty()
    reviewCount = ndb.IntegerProperty()

class Offer(Intangible):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Offer')

class StructuredValue(Intangible):
    itemtype = ndb.StringProperty(default=u'http://schema.org/StructuredValue')


class ContactPoint(StructuredValue):
    itemtype = ndb.StringProperty(default=u'http://schema.org/ContactPoint')
    contactType = ndb.StringProperty()
    email = ndb.StringProperty()
    faxNumber = ndb.StringProperty()
    telephone = ndb.StringProperty()

class PostalAddress(ContactPoint):
    itemtype = ndb.StringProperty(default=u'http://schema.org/PostalAddress')
    addressCountry = ndb.StructuredProperty(Country)
    addressLocality = ndb.StringProperty()
    addressRegion = ndb.StringProperty()
    postOfficeBoxNumber = ndb.StringProperty()
    postalCode = ndb.StringProperty()
    streetAddress = ndb.StringProperty()

class Organization(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Organization')
    address = ndb.StructuredProperty(PostalAddress)
    aggregateRating = ndb.StructuredProperty(AggregateRating)
    contactPoints = ndb.StructuredProperty(ContactPoint)
    email = ndb.StringProperty()
    events = ndb.StructuredProperty(Event)
    faxNumber = ndb.StringProperty()
    foundingDate = ndb.DateTimeProperty()
    interactionCount = ndb.StructuredProperty(UserInteraction, repeated=True)
    location = ndb.StructuredProperty(Place)
    reviews = ndb.StructuredProperty(Event, repeated=True)
    telephone = ndb.StringProperty()

class EducationalOrganization(Organization):
    itemtype = ndb.StringProperty(default=u'http://schema.org/EducationalOrganization')

class Affiliation(Intangible):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Position')
    endDate = ndb.DateTimeProperty()
    department = ndb.StringProperty()
    location = ndb.StructuredProperty(Place)
    organization = ndb.StructuredProperty(Organization)
    startDate = ndb.DateTimeProperty()

class Certification(PersonalAttribute):
    # Custom Type
    itemtype = ndb.StringProperty(default=u'http://schema.org/Certification')
    authority = ndb.StructuredProperty(Organization)
    endDate = ndb.DateTimeProperty()
    startDate = ndb.DateTimeProperty()
    value = ndb.StringProperty()

class Person(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Person')
    additionalName = ndb.StringProperty()
    awards = ndb.StringProperty()
    birthDate = ndb.DateTimeProperty()
    contactPoints = ndb.StructuredProperty(ContactPoint)
    deathDate = ndb.DateTimeProperty()
    email = ndb.StringProperty()
    familyName = ndb.StringProperty()
    faxNumber = ndb.StringProperty()
    gender = ndb.StringProperty()
    givenName = ndb.StringProperty()
    homeLocation = ndb.StructuredProperty(Place) # Place or ContactPoint
    honorificPrefix = ndb.StringProperty()
    honorificSuffix = ndb.StringProperty()
    interactionCount = ndb.StringProperty()
    jobTitle = ndb.StringProperty()
    nationality = ndb.StructuredProperty(Country)
    performerIn = ndb.StructuredProperty(Event)
    telephone = ndb.StringProperty()
    workLocation = ndb.StructuredProperty(Place) # Place or ContactPoint
    worksFor = ndb.StructuredProperty(Organization)
    # custom properties, these properties are not specified
    # in the schema.org spec
    provider = ndb.StringProperty()
    id = ndb.StringProperty()
    verified = ndb.BooleanProperty()
    locale = ndb.StringProperty()
    location = ndb.StructuredProperty(Place)
    utcOffset = ndb.StringProperty()
    dateCreated = ndb.DateTimeProperty()
    dateModified = ndb.DateTimeProperty()
    relationshipStatus = ndb.StringProperty(choices=[u'single',
          u'in_a_relationship', u'engaged', u'married', u'its_complicated',
          u'open_relationship', u'widowed', u'separated', u'divorced',
          u'in_domestic_partnership', u'in_civil_union'])



class CreativeWork(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/CreativeWork')
    about = ndb.StructuredProperty(Thing)
    accountablePerson = ndb.StructuredProperty(Person)
    aggregateRating = ndb.StructuredProperty(AggregateRating)
    alternativeHeadline = ndb.StringProperty()
#    audio = ndb.StructuredProperty(AudioObject)
    author = ndb.StructuredProperty(Person)
    awards = ndb.StringProperty()
    comment = ndb.StructuredProperty(UserComments)
    contentLocation = ndb.StructuredProperty(Place)
    contentRating = ndb.StringProperty()
    contributor = ndb.StructuredProperty(Person) # Or Organization
    copyrightHolder = ndb.StructuredProperty(Person) # Or Organization
    copyrightYear = ndb.IntegerProperty()
    creator = ndb.StructuredProperty(Person) # Or Organization
    dateCreated = ndb.DateTimeProperty()
    dateModified = ndb.DateTimeProperty()
    datePublished = ndb.DateTimeProperty()
    discussionUrl = ndb.StructuredProperty(URL)
    editor = ndb.StructuredProperty(Person)
    genre = ndb.StringProperty()
    headline = ndb.StringProperty()
    inLanguage = ndb.StringProperty()
    keywords = ndb.StringProperty()
    interactionCount = ndb.StructuredProperty(UserInteraction)
    isFamilyFriendly = ndb.BooleanProperty()
    mentions = ndb.StructuredProperty(Thing)
    offers = ndb.StructuredProperty(Offer)
    provider = ndb.StructuredProperty(Person) # Or Organization
    publisher = ndb.StructuredProperty(Organization)
    publishingPrinciples = ndb.StructuredProperty(URL)
    sourceOrganization = ndb.StructuredProperty(Organization)
    thumbnailUrl = ndb.StructuredProperty(URL)
    version = ndb.IntegerProperty()
#    video = ndb.StructuredProperty(VideoObject)

class MediaObject(CreativeWork):
    itemtype = ndb.StringProperty(default=u'http://schema.org/MediaObject')
#    associatedArticle = ndb.StructuredProperty(NewsArticle)
    bitrate	= ndb.StringProperty()
    contentSize	= ndb.StringProperty()
    contentURL = ndb.StructuredProperty(URL)
    duration = ndb.DateTimeProperty() #TODO Duration
    embedURL = ndb.StructuredProperty(URL)
    encodesCreativeWork = ndb.StructuredProperty(CreativeWork)
    encodingFormat	= ndb.StringProperty()
    expires = ndb.DateTimeProperty()
    height = ndb.DateTimeProperty() #TODO Duration
    playerType = ndb.StringProperty()
    regionsAllowed = ndb.StructuredProperty(Place)
    requiresSubscription = ndb.BooleanProperty()
    uploadDate = ndb.StringProperty()
#    width = ndb.StructuredProperty(Distance)

class Review(CreativeWork):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Review')
    itemReviewed = ndb.StructuredProperty(Thing)
    reviewBody = ndb.StringProperty()
    reviewRating = ndb.StructuredProperty(Rating)

class Product(Thing):
    itemtype = ndb.StringProperty(default=u'http://schema.org/Product')
    aggregateRating = ndb.StructuredProperty(AggregateRating)
    brand = ndb.StructuredProperty(Organization)
    manufacturer = ndb.StructuredProperty(Organization)
    model = ndb.StringProperty()
    offer = ndb.StructuredProperty(Offer)
    productID = ndb.StringProperty()
    reviews = ndb.StructuredProperty(Review)


# CreativeWork
CreativeWork.reviews = ndb.StructuredProperty(Review)
CreativeWork.associatedMedia	= ndb.StructuredProperty(MediaObject)
CreativeWork.encodings = ndb.StructuredProperty(MediaObject)

# Place
Place.address = ndb.StructuredProperty(PostalAddress)
Place.aggregateRating = ndb.StructuredProperty(AggregateRating)
Place._fix_up_properties()


# Person
Person.address = ndb.StructuredProperty(PostalAddress)
# Changed usage
Person.affiliation = ndb.LocalStructuredProperty(Affiliation)
Person.affiliations = ndb.LocalStructuredProperty(Affiliation, repeated=True)
Person.alumniOf = ndb.LocalStructuredProperty(EducationalOrganization, repeated=True)
Person.memberOf = ndb.LocalStructuredProperty(Organization, repeated=True)
Person.urls = ndb.StructuredProperty(URL, repeated=True)
Person.colleagues = ndb.StructuredProperty(Person, repeated=True)
Person.children = ndb.StructuredProperty(Person, repeated=True)
Person.follows = ndb.StructuredProperty(Person, repeated=True)
Person.knows = ndb.StructuredProperty(Person, repeated=True)
Person.parents = ndb.StructuredProperty(Person, repeated=True)
Person.relatedTo = ndb.StructuredProperty(Person, repeated=True)
Person.siblings = ndb.StructuredProperty(Person, repeated=True)
Person.spouse = ndb.StructuredProperty(Person, repeated=True)
# Custom
Person.accounts = ndb.StructuredProperty(Account, repeated=True)
Person.emails = ndb.StructuredProperty(Email, repeated=True)
Person.certifications = ndb.StructuredProperty(Certification, repeated=True)
Person.ims = ndb.StructuredProperty(IM, repeated=True)
Person.languagesSpoken = ndb.StructuredProperty(Language, repeated=True)
Person.skills = ndb.StructuredProperty(Skill, repeated=True)
Person._fix_up_properties()


# Organization
Organization.employees = ndb.LocalStructuredProperty(Person, repeated=True)
Organization.founders = ndb.LocalStructuredProperty(Person, repeated=True)
Organization.members = ndb.LocalStructuredProperty(Person, repeated=True)


# Education
EducationalOrganization.alumni = ndb.LocalStructuredProperty(Person, repeated=True)


# Affiliation
Affiliation.organization = ndb.LocalStructuredProperty(Organization)

# Event
Event.attendees = ndb.LocalStructuredProperty(Person)
# TODO: offer
Event.performers = ndb.LocalStructuredProperty(Person)
Event.subEvents = ndb.LocalStructuredProperty(Event)
Event.superEvent = ndb.LocalStructuredProperty(Event)
