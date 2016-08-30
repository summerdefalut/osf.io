from rest_framework import serializers as ser

from modularodm.exceptions import ValidationValueError

from api.base.exceptions import InvalidModelValueError, JSONAPIException, Conflict
from api.base.serializers import AllowMissing, JSONAPIRelationshipSerializer, HideIfDisabled
from website.models import User

from api.base.serializers import (
    JSONAPISerializer, LinksField, RelationshipField, DevOnly, IDField, TypeField, JSONAPIListField
)
from api.base.utils import absolute_reverse, get_user_auth

from framework.auth.views import send_confirm_email

class UserSerializer(JSONAPISerializer):
    filterable_fields = frozenset([
        'full_name',
        'given_name',
        'middle_names',
        'family_name',
        'id'
    ])
    non_anonymized_fields = ['type']
    id = IDField(source='_id', read_only=True)
    type = TypeField()
    full_name = ser.CharField(source='fullname', required=True, label='Full name', help_text='Display name used in the general user interface')
    given_name = ser.CharField(required=False, allow_blank=True, help_text='For bibliographic citations')
    middle_names = ser.CharField(required=False, allow_blank=True, help_text='For bibliographic citations')
    family_name = ser.CharField(required=False, allow_blank=True, help_text='For bibliographic citations')
    suffix = HideIfDisabled(ser.CharField(required=False, allow_blank=True, help_text='For bibliographic citations'))
    date_registered = HideIfDisabled(ser.DateTimeField(read_only=True))
    active = HideIfDisabled(ser.BooleanField(read_only=True, source='is_active'))


    twitter = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.twitter',
                                                           allow_blank=True, help_text='Twitter Handle'), required=False, source='social.twitter')))
    linkedin = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.linkedIn',
                                                            allow_blank=True, help_text='LinkedIn Account'), required=False, source='social.linkedIn')))
    impactstory = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.impactStory',
                                                               allow_blank=True, help_text='ImpactStory Account'), required=False, source='social.impactStory')))
    orcid = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.orcid',
                                                         allow_blank=True, help_text='ORCID'), required=False, source='social.orcid')))
    researcherid = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.researcherId',
                                                      allow_blank=True, help_text='ResearcherId Account'), required=False, source='social.researcherId')))
    researchgate = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.researchGate',
                                                      allow_blank=True, help_text='ResearchGate Account'), required=False, source='social.researchGate')))
    academia_institution = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.academiaInstitution',
                                                      allow_blank=True, help_text='AcademiaInstitution Field'), required=False, source='social.academiaInstitution')))
    academia_profile_id = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.academiaProfileID',
                                                      allow_blank=True, help_text='AcademiaProfileID Field'), required=False, source='social.academiaProfileID')))
    baiduscholar = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.baiduScholar',
                                                           allow_blank=True, help_text='Baidu Scholar Account'), required=False, source='social.baiduScholar')))
    ssrn = DevOnly(HideIfDisabled(AllowMissing(ser.CharField(required=False, source='social.ssrn',
                                                           allow_blank=True, help_text='SSRN Account'), required=False, source='social.ssrn')))
    timezone = HideIfDisabled(ser.CharField(required=False, help_text="User's timezone, e.g. 'Etc/UTC"))
    locale = HideIfDisabled(ser.CharField(required=False, help_text="User's locale, e.g.  'en_US'"))
    social = HideIfDisabled(LinksField(
        {
            'personal_website': 'personal_website_url',
            'github': 'github_url',
            'scholar': 'scholar_url',
            'twitter': 'twitter_url',
            'linkedin': 'linkedin_url',
            'impactStory': 'impactstory_url',
            'orcid': 'orcid_url',
            'researcherid': 'researcherid_url',
            'researchgate': 'researchgate_url',
            'academia_institution': 'academia_institution_url',
            'academia_profile_id': 'academia_profile_id_url',
            'baiduscholar': 'baiduscholar_url',
            'ssrn': 'ssrn_url',
        }
    ))
    links = HideIfDisabled(LinksField(
        {
            'html': 'absolute_url',
            'profile_image': 'profile_image_url',
        }
    ))

    nodes = HideIfDisabled(RelationshipField(
        related_view='users:user-nodes',
        related_view_kwargs={'user_id': '<pk>'},
        related_meta={'projects_in_common': 'get_projects_in_common'},
    ))

    registrations = DevOnly(HideIfDisabled(RelationshipField(
        related_view='users:user-registrations',
        related_view_kwargs={'user_id': '<pk>'},
    )))

    institutions = HideIfDisabled(RelationshipField(
        related_view='users:user-institutions',
        related_view_kwargs={'user_id': '<pk>'},
        self_view='users:user-institutions-relationship',
        self_view_kwargs={'user_id': '<pk>'},
    ))

    education = DevOnly(HideIfDisabled(RelationshipField(
        related_view='users:user-education',
        related_view_kwargs={'user_id': '<pk>'},
    )))

    employment = DevOnly(HideIfDisabled(RelationshipField(
        related_view='users:user-employment',
        related_view_kwargs={'user_id': '<pk>'},
    )))

    def github_url(self, obj):
        if obj.social['github']:
            return 'http://github.com/{}/'.format(obj.social['github'])
        return ' '

    def scholar_url(self, obj):
        if obj.social['scholar']:
            return 'http://scholar.google.com/citations?user={}'.format(obj.social['scholar'])
        return ' '

    def personal_website_url(self, obj):
        return obj.social['profileWebsites'] if obj.social['profileWebsites'] else ' '

    def twitter_url(sel, obj):
        if obj.social['twitter']:
            return 'http://twitter.com/{}'.format(obj.social['twitter'])
        return ' '

    def linkedin_url(self, obj):
        if obj.social['linkedIn']:
            return 'http://twitter.com/{}'.format(obj.social['linkedIn'])
        return ' '

    def orcid_url(self, obj):
        if obj.social['orcid']:
            return 'https://www.linkedin.com/{}'.format(obj.social['orcid'])
        return ' '

    def impactstory_url(self, obj):
        if obj.social['impactStory']:
            return 'https://impactstory.org/{}'.format(obj.social['impactStory'])
        return ' '

    def researcherid_url(self, obj):
        if obj.social['researcherId']:
            return 'http://researcherid.com/rid/{}'.format(obj.social['researcherId'])
        return ' '

    def researchgate_url(self, obj):
        if obj.social['researchGate']:
            return 'https://researchgate.net/profile/{}'.format(obj.social['researchGate'])
        return ' '

    def academia_institution_url(self, obj):
        if obj.social['academiaInstitution']:
            return 'https://{}'.format(obj.social['academiaInstitution'])
        return ' '

    def academia_profile_id_url(self, obj):
        if obj.social['academiaProfileID']:
            return '.academia.edu/{}'.format(obj.social['academiaProfileID'])
        return ' '

    def baiduscholar_url(self, obj):
        if obj.social['baiduScholar']:
            return 'http://xueshu.baidu.com/scholarID/{}'.format(obj.social['baiduScholar'])
        return ' '

    def ssrn_url(self, obj):
        if obj.social['ssrn']:
            return 'http://twitter.com/{}'.format(obj.social['ssrn'])
        return ' '

    class Meta:
        type_ = 'users'

    def get_projects_in_common(self, obj):
        user = get_user_auth(self.context['request']).user
        if obj == user:
            return len(user.contributor_to)
        return len(obj.get_projects_in_common(user, primary_keys=True))

    def absolute_url(self, obj):
        if obj is not None:
            return obj.absolute_url
        return None

    def get_absolute_url(self, obj):
        return absolute_reverse('users:user-detail', kwargs={'user_id': obj._id})

    def profile_image_url(self, user):
        size = self.context['request'].query_params.get('profile_image_size')
        return user.profile_image_url(size=size)

    def update(self, instance, validated_data):
        assert isinstance(instance, User), 'instance must be a User'
        for attr, value in validated_data.items():
            if 'social' == attr:
                for key, val in value.items():
                    instance.social[key] = val
            else:
                setattr(instance, attr, value)
        try:
            instance.save()
        except ValidationValueError as e:
            raise InvalidModelValueError(detail=e.message)
        return instance


class UserCreateSerializer(UserSerializer):
    username = ser.EmailField(required=False)

    def create(self, validated_data):
        username = validated_data.get('username', '').lower() or None
        full_name = validated_data.get('fullname')
        if not full_name:
            raise JSONAPIException('A `full_name` is required to create a user.')

        user = User.create_unregistered(full_name, email=username)
        user.registered_by = self.context['request'].user
        if username:
            user.add_unconfirmed_email(user.username)

        try:
            user.save()
        except ValidationValueError:
            raise Conflict('User with specified username already exists.')

        if self.context['request'].GET.get('send_email', False) and username:
            send_confirm_email(user, user.username)

        return user

class UserAddonSettingsSerializer(JSONAPISerializer):
    """
    Overrides UserSerializer to make id required.
    """
    id = ser.CharField(source='config.short_name', read_only=True)
    user_has_auth = ser.BooleanField(source='has_auth', read_only=True)

    links = LinksField({
        'self': 'get_absolute_url',
        'accounts': 'account_links'
    })

    class Meta:
        type_ = 'user_addons'

    def get_absolute_url(self, obj):
        user_id = self.context['request'].parser_context['kwargs']['user_id']
        return absolute_reverse(
            'users:user-addon-detail',
            kwargs={
                'user_id': user_id,
                'provider': obj.config.short_name
            }
        )

    def account_links(self, obj):
        # TODO: [OSF-4933] remove this after refactoring Figshare
        if hasattr(obj, 'external_accounts'):
            return {
                account._id: {
                    'account': absolute_reverse('users:user-external_account-detail', kwargs={'user_id': obj.owner._id, 'provider': obj.config.short_name, 'account_id': account._id}),
                    'nodes_connected': [n.absolute_api_v2_url for n in obj.get_attached_nodes(account)]
                }
                for account in obj.external_accounts
            }
        return {}

class UserDetailSerializer(UserSerializer):
    """
    Overrides UserSerializer to make id required.
    """
    id = IDField(source='_id', required=True)


class RelatedInstitution(JSONAPIRelationshipSerializer):
    id = ser.CharField(required=False, allow_null=True, source='_id')
    class Meta:
        type_ = 'institutions'

    def get_absolute_url(self, obj):
        return obj.absolute_api_v2_url


class UserInstitutionsRelationshipSerializer(ser.Serializer):

    data = ser.ListField(child=RelatedInstitution())
    links = LinksField({'self': 'get_self_url',
                        'html': 'get_related_url'})

    def get_self_url(self, obj):
        return absolute_reverse('users:user-institutions-relationship', kwargs={'user_id': obj['self']._id})

    def get_related_url(self, obj):
        return absolute_reverse('users:user-institutions', kwargs={'user_id': obj['self']._id})

    def get_absolute_url(self, obj):
        return obj.absolute_api_v2_url

    class Meta:
        type_ = 'institutions'


class UserEducationSerializer(ser.Serializer):

    id = IDField(source='_id', required=False)
    institution = ser.CharField(required=False, allow_blank=True)
    department = ser.CharField(required=False, allow_blank=True)
    degree = ser.CharField(required=False, allow_blank=True)
    start_month = ser.CharField(source='startMonth',required=False, allow_blank=True)
    start_year = ser.CharField(source='startYear',required=False, allow_blank=True)
    end_month = ser.CharField(source='endMonth',required=False, allow_blank=True)
    end_year = ser.CharField(source='endYear',required=False, allow_blank=True)
    ongoing = ser.BooleanField(required=False)

    class Meta:
        type_ = 'education'

    def absolute_url(self, obj):
        if obj is not None:
            return obj.absolute_url
        return None


class UserEmploymentSerializer(ser.Serializer):

    id = IDField(source='_id', required=False)
    institution = ser.CharField(required=False, allow_blank=True)
    department = ser.CharField(required=False, allow_blank=True)
    title = ser.CharField(required=False, allow_blank=True)
    start_month = ser.CharField(source='startMonth', required=False, allow_blank=True)
    start_year = ser.CharField(source='startYear', required=False, allow_blank=True)
    end_month = ser.CharField(source='endMonth', required=False, allow_blank=True)
    end_year = ser.CharField(source='endYear', required=False, allow_blank=True)
    ongoing = ser.BooleanField(required=False)

    class Meta:
        type_ = 'employment'

    def absolute_url(self, obj):
        if obj is not None:
            return obj.absolute_url
        return None

