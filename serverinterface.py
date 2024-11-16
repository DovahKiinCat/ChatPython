import socket
import threading
import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

kivy.require('2.1.0')

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class ChatInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatInterface, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.chat_log = Label(text='', halign='left', valign='top', size_hint_y=None, markup=True, text_size=(Window.width, None))
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

        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ''
        porta = 0
        self.socket_servidor.bind((host, porta))
        self.socket_servidor.listen(5)
        
        self.client_sockets = []

        threading.Thread(target=self.aceitar_conexoes, daemon=True).start()

    def _update_chat_log_height(self, *_):
        self.chat_log.text_size = (self.chat_log.width, None)
        self.chat_log.height = self.chat_log.texture_size[1]
        self.chat_log.canvas.ask_update()
        self.scroll_view.scroll_y = 0
    
    def aceitar_conexoes(self):
        while True:
            socket_cliente, endereco_cliente = self.socket_servidor.accept()
            self.client_sockets.append(socket_cliente)
            threading.Thread(target=self.tratar_cliente, args=(socket_cliente,), daemon=True).start()

    def tratar_cliente(self, socket_cliente):
        while True:
            try:
                dados = socket_cliente.recv(1024)
                if not dados:
                    break
                mensagem = dados.decode('utf-8')
                Clock.schedule_once(lambda dt: self.update_chat(mensagem, '[color=ff3333]Cliente[/color]: '))
            except ConnectionResetError:
                break
        socket_cliente.close()
        self.client_sockets.remove(socket_cliente)

    def send_message(self, instance):
        mensagem = self.message_input.text
        if mensagem.strip() == "":
            return

        self.update_chat(mensagem, '[color=33ff33]Você[/color]: ')
        for client_socket in self.client_sockets:
            try:
                client_socket.sendall(mensagem.encode('utf-8'))
            except BrokenPipeError:
                self.client_sockets.remove(client_socket)
        self.message_input.text = ''

    def update_chat(self, message, prefix=''):
        self.chat_log.text += f"{prefix}{message}\n"
        Clock.schedule_once(lambda dt: self.scroll_view.scroll_y == 0)

class ChatServer(App):
    def build(self):
        return ChatInterface()

if __name__ == '__main__':
    ChatServer().run()
