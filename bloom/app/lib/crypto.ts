import * as jose from 'jose'

const getSecret = () => {
  const secret = process.env.NEXT_PUBLIC_ENCRYPTION_KEY
  if (!secret) {
    throw new Error('NEXTAUTH_SECRET is not set')
  }
  return new TextEncoder().encode(secret)
}

export async function encryptPassword(password: string): Promise<string> {
  try {
    const secret = getSecret()
    const jwt = await new jose.SignJWT({ password })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('2m')
      .sign(secret)
    
    return jwt
  } catch (error) {
    console.error('Encryption error:', error)
    throw new Error('Failed to encrypt password')
  }
}

export async function decryptPassword(token: string): Promise<string | null> {
  try {
    const secret = getSecret()
    const { payload } = await jose.jwtVerify(token, secret)
    return payload.password as string
  } catch (error) {
    console.error('Decryption error:', error)
    return null
  }
} 