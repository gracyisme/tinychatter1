from flask import Flask, request
import requests

app = Flask(__name__)
 
# Mục đích của app này là dùng flask aka web application để listen các sự kiện từ hook của facebook trả về, sau đó reply lại với hook của facebook thông qua đó gửi được message cho người dùng

# Đây là page access_token lấy từ https://developers.facebook.com/.
PAGE_ACCESS_TOKEN = 'PAGE_ACCESS_TOKEN'
# Gắn access token cho graph api messenger để có thể sử dụng.
API = "https://graph.facebook.com/v14.0/me/messages?access_token="+PAGE_ACCESS_TOKEN

# Xác thực web_hooks với application 
@app.route("/", methods=['GET'])
def fbverify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token")== "anystring":
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200
    return "Nothing happened", 200

# Render response cho người dùng 
def getOpenConversationText(response, sender_id):
    return getQuickChoicesResponse(response=getTextResponse(response= response, text='Xin chào, mình là bot và mình sẽ giúp bạn giải đáp thắc mắc hôm nay nhé !', sender_id=sender_id), sender_id=sender_id)

# Render text response với text là nội dung trả về để hiển thị, sender_id là id của người dùng nhắn tin với chatbot 
def getTextResponse(response, text: str, sender_id):
        request_body = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": text
            }
        }
        response = requests.post(API, json=request_body).json()
        return response

# Render quick choices để trả về cho người dùng (format payload có thể xem tại đây: https://developers.facebook.com/docs/messenger-platform/send-messages/quick-replies)
def getQuickChoicesResponse(response, sender_id):
    request_body = {
                "recipient": {
                    "id": sender_id
                },
                "messaging_type": "RESPONSE",
                "message": {
                    "text": "Bạn cho mình biết thắc mắc của bạn liên quan đến lĩnh vực nào được chứ ?",
                    "quick_replies": [
                        {
                            "content_type": "text",
                            "title": "Thông tin công ty",
                            "payload": "<POSTBACK_PAYLOAD>",
                        }, {
                            "content_type": "text",
                            "title": "Thông tin thanh toán",
                            "payload": "<POSTBACK_PAYLOAD>",
                        },
                         {
                            "content_type": "text",
                            "title": "Thông tin vận chuyển",
                            "payload": "<POSTBACK_PAYLOAD>",
                        },
                           {
                            "content_type": "text", 
                            "title": "Thông tin hàng hóa",
                            "payload": "<POSTBACK_PAYLOAD>", # Mục đích của trường này là để khi người dùng chọn option mình có thể định nghĩa loại option người dùng gửi trả về web app để phản hồi cho sau này
                        }
                    ]
                }
            }
    response = requests.post(API, json=request_body).json()
    return response # Response trả về cho bên phía web_hooks theo đúng định dạng của facebook quy định, thông qua đó có thể render các thể loại message tới người dùng

# Nơi tiếp nhận messenger từ người dùng thông qua webhooks 
@app.route("/", methods=['POST'])
def fbwebhook():
    data = request.get_json() # Data webhook gửi lên dạng raw
    print(data) 
    try:
        response = any;
        # Format để lấy được message (có thể dùng message để đọc ra được người dùng đã nhắn gì, ở đây thì chưa cần)
        message = data['entry'][0]['messaging'][0]['message']
        # Format để lấy id aka sender_id sẽ được sử dụng trong các function bên dưới
        sender_id = data['entry'][0]['messaging'][0]['sender']['id'] 
        return getOpenConversationText(response=response, sender_id= sender_id)
    except:
        # Phần này để bắt lỗi và đảm bảo là khi có lỗi xảy ra, chatbot vẫn có thể hoạt động và không bị fail
        try:
            mess = data['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['url']
            print("for url-->",mess)
            json_path = requests.get(mess)
            filename = mess.split('?')[0].split('/')[-1]
            open(filename, 'wb').write(json_path.content)
        except:
            print("Noot Found-->")
 
    return 'ok'

# Hàm main để khởi chạy ứng dụng
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
