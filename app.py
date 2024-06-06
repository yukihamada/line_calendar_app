

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Google OAuth 2.0の設定

# LINE Messaging APIの設定
LINE_CHANNEL_ACCESS_TOKEN = 'DUMMY_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'DUMMY_CHANNEL_SECRET'

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def oauth2callback():
    state = session['state']


        'client_secret.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('calendar'))


@app.route('/calendar')
def calendar():
    if 'credentials' not in session:
        return redirect('login')

    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)

    events_result = service.events().list(calendarId='primary').execute()
    events = events_result.get('items', [])

    event_list = '<table><tr><th>Event</th><th>Start</th><th>End</th></tr>'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        event_list += f'<tr><td>{event["summary"]}</td><td>{start}</td><td>{end}</td></tr>'
    event_list += '</table>'

    return event_list

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


# LINE Messaging APIの設定
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    return 'Hello, this is the LINE Calendar Integration App!'

if __name__ == '__main__':
    app.run(port=5000)

