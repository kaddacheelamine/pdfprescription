import datetime
import pytz
import re
import sys
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from endesive import pdf

def load_pfx(file_path, password):
    with open(file_path, 'rb') as fp:
        return pkcs12.load_key_and_certificates(fp.read(), password.encode(), backends.default_backend())

def get_rdns_names(rdns):
    OID_NAMES = {
        NameOID.COMMON_NAME: 'CN',
        NameOID.COUNTRY_NAME: 'C',
    }
    names = {OID_NAMES[oid]: '' for oid in OID_NAMES}
    for rdn in rdns:
        for attr in rdn._attributes:
            if attr.oid in OID_NAMES:
                names[OID_NAMES[attr.oid]] = attr.value
    return names

def sign_pdf(pfx_path, password, pdf_path, output_path=None, page=1, coords=(250, 5, 550, 150)):
    try:
        p12pk, p12pc, p12oc = load_pfx(pfx_path, password)
        names = get_rdns_names(p12pc.subject.rdns)
        date = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S+00\'00\'')
        signature = f"rushita platform \n digitally signed Dr startup dz \nDATE: {date}"
        dct = {
            'sigflags': 3,
            'sigpage': page - 1,
            'contact': 'email@example.com',
            'location': 'Location',
            'signingdate': date,
            'reason': 'Signed digitally',
            'signature': signature,
            'signaturebox': tuple(coords),
        }
        with open(pdf_path, 'rb') as f:
            datau = f.read()
        datas = pdf.cms.sign(datau, dct, p12pk, p12pc, p12oc, 'sha256')
        output_file = output_path if output_path else pdf_path.replace('.pdf', '_signed.pdf')
        with open(output_file, 'wb') as f:
            f.write(datau)
            f.write(datas)
        print(f"PDF signed successfully: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error signing PDF: {e}", file=sys.stderr)
        return None
    
