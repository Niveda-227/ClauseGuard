"""Label order matches the LexGLUE UNFAIR-ToS release."""
LABELS = (
    'Limitation of liability', 'Unilateral termination', 'Unilateral change',
    'Content removal', 'Contract by using', 'Choice of law', 'Jurisdiction', 'Arbitration',
)
EXPLANATIONS = {
    'Limitation of liability': 'Limits the kinds or amount of compensation the provider may owe.',
    'Unilateral termination': 'Lets the provider end or suspend the agreement or account.',
    'Unilateral change': 'Lets the provider change the agreement or service conditions.',
    'Content removal': 'Lets the provider remove or restrict content.',
    'Contract by using': 'Treats using the service as accepting the terms.',
    'Choice of law': 'Specifies which laws govern the agreement.',
    'Jurisdiction': 'Specifies the courts or location for disputes.',
    'Arbitration': 'Provides for resolving disputes through arbitration.',
}
NOTICE = ('Flags identify categories to review. They do not determine legality or safety. '
          'Unflagged text can still matter. Scores are uncalibrated model outputs, not legal-risk probabilities.')
