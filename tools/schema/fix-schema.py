# Correct the six invalid structured-data items flagged by the site audit.
#
# Rule applied, derived from the schema.org vocabulary rather than guesswork:
#   availableService  -> valid only on Hospital, MedicalClinic, Physician
#   medicalSpecialty  -> valid only on Hospital, MedicalClinic, MedicalOrganization, Physician
#   priceRange        -> valid only on LocalBusiness (and its subtypes)
#
# So a node's type is chosen by what it actually is:
#   a real office with a postal address -> MedicalClinic
#       (subclass of BOTH MedicalBusiness and MedicalOrganization, so it inherits
#        LocalBusiness properties AND the medical ones - every property validates)
#   an umbrella / state-level entity with no address -> stays MedicalOrganization,
#       and its service moves from availableService to makesOffer, which IS valid
#       on Organization. No information is lost.
#
# priceRange "$$" is dropped everywhere: it is only "recommended" by Google, and a
# price tier is meaningless for insurance-billed care.
import json, sys, copy

def to_clinic(node):
    node['@type'] = 'MedicalClinic'
    node.pop('priceRange', None)
    return node

def service_to_offer(node):
    svc = node.pop('availableService', None)
    if svc is not None:
        node['makesOffer'] = {'@type': 'Offer', 'itemOffered': svc}
    node.pop('priceRange', None)
    return node

# node @id -> transform
CLINIC = {
    'https://www.mastermindbehavior.com/contact#office-lakewood',
    'https://www.mastermindbehavior.com/contact#office-macon',
}
ORG = {
    'https://www.mastermindbehavior.com/#organization',
    'https://www.mastermindbehavior.com/aba-therapy-in-north-carolina#organization-north-carolina',
}

def fix(doc):
    doc = copy.deepcopy(doc)
    for node in doc.get('@graph', []):
        i = node.get('@id')
        if i in CLINIC and node.get('@type') == 'MedicalBusiness':
            to_clinic(node)
        elif i in ORG and node.get('@type') == 'MedicalOrganization':
            # only the full node carries these; the stub references do not
            if 'availableService' in node or 'priceRange' in node:
                service_to_offer(node)
    return doc

if __name__ == '__main__':
    src = json.load(open(sys.argv[1]))
    json.dump({k: fix(v) for k, v in src.items()}, open(sys.argv[2], 'w'), indent=1)
    print('wrote', sys.argv[2])
