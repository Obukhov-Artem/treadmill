boolean answer(boolean stringComplete, String txtMsg, boolean treadmill_init, boolean itreadmill) {
  if (stringComplete)
    {
      if (txtMsg == "treadmill")
      {
        treadmill_init = true;
        }
      if (txtMsg == "d"){
        itreadmill = false;
        question();
      }
      else
      treadmill_init = false;
  

}
