import time
from typing import Dict, Optional
from db.schema import SessionLocal, IntegrationToken
import requests


def get_token(client_id: str, client_secret: str, token_url: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        rec = db.query(IntegrationToken).filter_by(client_id=client_id).first()
        if rec and rec.expires_at > int(time.time()):
            return {"access_token": rec.access_token, "expires_at": rec.expires_at}
        resp = requests.post(token_url, data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}, timeout=10)
        data = resp.json()
        token = data.get("access_token")
        expires = int(time.time()) + int(data.get("expires_in", 3600))
        if rec:
            rec.access_token = token
            rec.expires_at = expires
        else:
            rec = IntegrationToken(client_id=client_id, access_token=token, expires_at=expires)
            db.add(rec)
        db.commit()
        return {"access_token": token, "expires_at": expires}
    finally:
        db.close()
