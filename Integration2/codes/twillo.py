from twilio.rest import Client
import keys

client=Client(keys.account_sid,keys.auth_token)

message = client.messages.create(
    body="https://pathfinder-djqp8utbcjvh5vxccjh7mm.streamlit.app/",
    from_=keys.twilio_number,
    to=keys.target_number
)

print(message.body)
