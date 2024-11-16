import socket
import threading
import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

kivy.require('2.1.0')

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class ChatInterface(BoxLayout):

    def __init__(self, **kwargs):
        super(ChatInterface, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.chat_log = Label(text='', halign='left', valign='top', size_hint_y=None, markup=True)
        self.chat_log.bind(size=self._update_chat_log_height)

        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.scroll_view.add_widget(self.chat_log)

        self.add_widget(self.scroll_view)
        
        self.input_layout = BoxLayout(size_hint=(1, 0.2), orientation='horizontal')

        self.message_input = TextInput(size_hint=(0.8, 1), multiline=False, hint_text='Digite sua mensagem...')
        self.input_layout.add_widget(self.message_input)

        self.send_button = Button(text='Enviar', size_hint=(0.2, 1))
        self.send_button.bind(on_press=self.send_message)
        self.input_layout.add_widget(self.send_button)

        self.add_widget(self.input_layout)

        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ''
        porta = 0
        self.socket_cliente.connect((host, porta))

        self.update_thread = threading.Thread(target=self.server_msg)
        self.update_thread.start()

    def _update_chat_log_height(self, *_):
        self.chat_log.text_size = (self.chat_log.width, None)
        self.chat_log.height = self.chat_log.texture_size[1]
        self.chat_log.canvas.ask_update()
        self.scroll_view.scroll_y = 0

    def send_message(self, instance):
        mensagem = self.message_input.text
        if mensagem.strip() == "":
            return

        self.update_chat(mensagem, '[color=33ff33]Você[/color]: ')
        self.socket_cliente.sendall(mensagem.encode('utf-8'))
        self.message_input.text = ''

    def server_msg(self):
        while True:
            try:
                dados_servidor = self.socket_cliente.recv(1024)
                if not dados_servidor:
                    break
                mensagem_servidor = dados_servidor.decode('utf-8')
                Clock.schedule_once(lambda dt: self.update_chat(mensagem_servidor, '[color=ff3333]Servidor[/color]: '))
            except ConnectionResetError:
                break
        self.socket_cliente.close()

    def update_chat(self, message, prefix=''):
        self.chat_log.text += f"{prefix}{message}\n"
        Clock.schedule_once(lambda dt: self.scroll_view.scroll_y == 0)

class ChatClient(App):
    def build(self):
        return ChatInterface()

if __name__ == '__main__':
    ChatClient().run()
