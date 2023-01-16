from email.message import EmailMessage
import smtplib
class EmailSender:

    def __init__(self) -> None:
        self.msg = EmailMessage()
        self.email = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.username = "spotifymonthlyupdate@gmail.com"
        password = ""
        self.email.login(self.username, password)

    def send_email(self, top_tracks, top_artists, top_genres, email):
        """
        Sends an email to the user of their last months top songs, artists and genres.
        """
        message = "Your top tracks of the month:\n"
        for i, track in enumerate(top_tracks):
            current_num = i+1
            song = track[0]
            message += f"{current_num}. {song} by "

            artists = track[1]
            last_artist = len(artists) -1

            for i,artist in enumerate(artists):
                message += artist
                if i != last_artist:
                    message +=", "

            message += "\n"
        message += "\nYour top artists of the month:\n"
        for i, artist in enumerate(top_artists):
            current_num = i+1
            message += f"{current_num}. {artist[0]}\n"
        
        message += f"\nYour top genres of the month:\n"
        for i, genre in enumerate(top_genres):
            current_num = i+1
            message += f"{current_num}. {genre[0]}\n"

        
        self.msg.set_content(message)
        self.msg['subject'] = "Monthly Update"
        self.msg['to'] = email
        self.msg['from'] = self.username
        self.email.send_message(self.msg)