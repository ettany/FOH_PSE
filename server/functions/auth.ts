import { Handler } from '@netlify/functions';
import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import User from '../src/models/user.model'; // Adjust the path according to your structure
import axios from 'axios';

dotenv.config();

const jwtSecret = process.env.STOTRA_JWT_SECRET;
const turnstileSecret = process.env.STOTRA_TURNSTILE_SECRET;

const signup: Handler = async (event) => {
  const reqBody = JSON.parse(event.body || '{}');

  // Validate request body
  if (!reqBody.username || !reqBody.password) {
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Content can not be empty!' }),
    };
  }

  try {
    await validateTurnstile(reqBody['cf-turnstile-response']);

    const newUser = new User({
      username: reqBody.username,
      password: bcrypt.hashSync(reqBody.password, 8),
      watchlist: [],
      ledger: [],
      positions: [],
      cash: 100_000,
    });

    const user = await newUser.save();
    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'User was registered successfully!' }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ message: error.message }),
    };
  }
};

const login: Handler = async (event) => {
  const reqBody = JSON.parse(event.body || '{}');

  try {
    await validateTurnstile(reqBody['cf-turnstile-response']);

    const user = await User.findOne({ username: reqBody.username });

    if (!user) {
      return {
        statusCode: 404,
        body: JSON.stringify({ message: 'User Not found.' }),
      };
    }

    const passwordIsValid = bcrypt.compareSync(reqBody.password, user.password);

    if (!passwordIsValid) {
      return {
        statusCode: 401,
        body: JSON.stringify({
          accessToken: null,
          message: 'Incorrect password',
        }),
      };
    }

    const token = jwt.sign({ id: user.id }, jwtSecret!, {
      algorithm: 'HS256',
      allowInsecureKeySizes: true,
      expiresIn: '7 days',
    });

    return {
      statusCode: 200,
      body: JSON.stringify({
        id: user._id,
        username: user.username,
        accessToken: token,
      }),
    };
  } catch (error) {
    return {
      statusCode: 400,
      body: JSON.stringify({ message: error.message }),
    };
  }
};

const validateTurnstile = async (token: string): Promise<any> => {
  if (!turnstileSecret) {
    throw new Error('Turnstile secret not found');
  }

  const res = await axios.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    secret: turnstileSecret,
    response: token,
  });

  if (res.data.success) {
    return true;
  } else {
    throw new Error("Can't validate turnstile token: " + res.data['error-codes']);
  }
};

// Exporting the handler
export { signup, login };
