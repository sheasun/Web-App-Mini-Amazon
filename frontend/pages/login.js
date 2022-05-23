import {useEffect, useState} from 'react';
import {useRouter} from 'next/router';
import WarningDialog from '../components/warningDialog';
import Cookies from 'js-cookie';

export default function Login({token}) {

  console.log(token);

  const router = useRouter();
  const [warningDialogOpen, setWarningDialogOpen] = useState(false);
  const [warningMessage, setWarningMessage] = useState(null);
    /**
   * set warning message and open dialog
   * @param {String} warningMessage 
   */
     const setErrorMessageAndOpenDialog = (warningMessage) => {
      setWarningMessage(warningMessage);
      setWarningDialogOpen(true);
      console.log(warningMessage);
    }
  
    /**
     * purge warning message and close dialog
     */
    const resetErrorMessageAndCloseDialog = () => {
      setWarningMessage(null);
      setWarningDialogOpen(false);
    }

  const tryLogin = async event => {
    event.preventDefault();

    const email = event.target.email.value;
    const password = event.target.password.value;

    let formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    const result =  await fetch(`${process.env.httpHost}/login`, {
      method: "post",
      body: formData,
    });
    const status = result.status;
    const response = await result.json();

    if(status != 200){
      setErrorMessageAndOpenDialog(response['message']);
      return;
    }

    Cookies.set('token', response['token']);
    router.push('/');
  }

  return (
    <div className='flex flex-col items-center h-screen space-y-2'>
      <WarningDialog _open={warningDialogOpen} _close={()=>resetErrorMessageAndCloseDialog()} _message={warningMessage}/>
      <p className='mt-7 font-bold text-lg'>
        Log In to Your Account
      </p>
      <form id='loginForm' onSubmit={tryLogin} className='table'>
        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='email'>Email: </label>
          <input className='table-cell my-1 border-2' name='email' type='text' required></input>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='password'>Password: </label>
          <input className='table-cell my-1 border-2' name='password' type='password' required></input><br/>
        </p>
      </form>

      <div className='flex flex-row space-x-5'>
        <button form='loginForm' type='submit' className='btn'>
          Log In
        </button>
        <button className='btn' onClick={() => {router.push('/signup')}}>
          Sign Up
        </button>
      </div>
    </div>
  )
}


export async function getServerSideProps({req, res}){
  const token = req.cookies.token || null;
  if(token){
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    }
  }

  return {
    props: {
      token: token,
    }
  }
}
