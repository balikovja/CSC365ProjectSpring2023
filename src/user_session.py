
# TODO: use session keys

# TODO: remove public user
logged_in_users = [2]


#TODO: login time out

def check_logged_in(user_id):
	return user_id in logged_in_users

def login(user_id):
	if user_id in logged_in_users:
		return -1
	logged_in_users.append(user_id)
	return 0

def logout(user_id):
	if user_id in logged_in_users:
		logged_in_users.remove(user_id)
		return 0
	return -1
