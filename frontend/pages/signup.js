import {useRouter} from 'next/router';
import { useState } from 'react';

import WarningDialog from '../components/warningDialog';

export default function Signup(){
  
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

  /**
   * try sign up a user
   * @param {event} event form buttom submit event
   * @returns 
   */
  const trySignUp = async event =>{
    event.preventDefault();

    const email = event.target.email.value;
    const name = event.target.name.value;
    const upsName = event.target.upsName.value;
    const password = event.target.password.value;
    const confirmedPassword = event.target.confirm_password.value;
    const locationX = event.target.location_x.value;
    const locationY = event.target.location_y.value;

    // error: email not conforming regex
    const regexEmail = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if (!email.match(regexEmail)) {
      const warningMessage = "email not in the correct format";
      setErrorMessageAndOpenDialog(warningMessage);
      return;
    }

    // error: password not confirmed
    if(password != confirmedPassword){
      const warningMessage = "password not the same";
      setErrorMessageAndOpenDialog(warningMessage);
      return;
    }

    // create form, post request and await response
    let formData = new FormData();
    formData.append("email", email);
    formData.append("name", name);
    formData.append("upsName", upsName);
    formData.append("password", password);
    formData.append("location_x", locationX);
    formData.append("location_y", locationY);

    const result =  await fetch(`${process.env.httpHost}/signup`, {
      method: "post",
      body: formData,
    });
    const status = result.status;
    const response = await result.json();
    console.log(response["message"])

    // success: user signed up
    if(status === 200){
      router.push("/login");
    }
    // error: user exist
    else if(status === 409){
      const warningMessage = "email already taken";
      setErrorMessageAndOpenDialog(warningMessage);
      return;
    }
  }

  return(
    <div className='flex flex-col items-center h-screen space-y-2'>
      <WarningDialog _open={warningDialogOpen} _close={()=>resetErrorMessageAndCloseDialog()} _message={warningMessage}/>
      <p className='mt-7 font-bold text-lg'>Sign Up</p>
      <form id='signUpForm' onSubmit={trySignUp} className='table'>
        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='email'>Email: </label>
          <input className='table-cell my-1 border-2' name='email' type='text' required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='name'>Name: </label>
          <input className='table-cell my-1 border-2' name='name' type='text' required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='upsName'>UPS Name: </label>
          <input className='table-cell my-1 border-2' name='upsName' type='text'></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='location_x'>Location X: </label>
          <input className='table-cell my-1 border-2' name='location_x' type='number' required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='location_y'>Location Y: </label>
          <input className='table-cell my-1 border-2' name='location_y' type='number' required></input><br/>
        </p>
        
        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='password'>Password: </label>
          <input className='table-cell my-1 border-2' name='password' type='password' required></input><br/>
        </p>

        <p className='table-row space-x-2'>
          <label className='table-cell' htmlFor='confirm_password'>Confirm Password: </label>
          <input className='table-cell my-1 border-2' name='confirm_password' type='password' required></input><br/>
        </p>

      </form>

      <div className='flex flex-row space-x-5'>
        <button form='signUpForm' type='submit' className='btn'>
          Sign Up
        </button>
        <button onClick={() => {router.push('/login')}} className='btn'>
          Back
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