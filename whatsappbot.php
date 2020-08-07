<?php
{
                        class whatsAppBot{
                        //specify instance URL and token
                        var $APIurl = 'https://eu97.chat-api.com/instance141420/';
                        var $token = 'gl0zym0gtjvs7xsw';

                        public function __construct(){
                        //get the JSON body from the instance
                        $json = file_get_contents('php://input');
                        $decoded = json_decode($json,true);

                        //write parsed JSON-body to the file for debugging
                        ob_start();
                        var_dump($decoded);
                        $input = ob_get_contents();
                        ob_end_clean();
                        file_put_contents('input_requests.log',$input.PHP_EOL,FILE_APPEND);

                        if(isset($decoded['messages'])){
                        //check every new message
                        foreach($decoded['messages'] as $message){
                        //delete excess spaces and split the message on spaces. The first word in the message is a command, other words are parameters
                        $text = $message['body'];
                        //current message shouldn't be send from your bot, because it calls recursion
                        if(!$message['fromMe']){
                             switch(mb_strtolower($text)){
                            case 'hi':  {$this->askHelp($message['chatId'],$message['senderName']); break;}
                            case 'about':{$this->askHelp($message['chatId'],$message['senderName']); break;}
                            case 'help': {$this->askHelp($message['chatId'],$message['senderName']); break;}
                            default:{$this->checkLengthOfText($message['chatId'],$message['body']); break;}
                            }}}}}



                        public function checkLengthOfText($chatId,$message) {
                            // if less that 100 then send article is too short to be analyzed
                            if (str_word_count($message) < 60) {
                                $erMess = " ⚠️ Sorry , the article you have sent is too short to be analyzed. \n\n Please try again by sending an article with at least 100 words\n";
                                $this->sendMessage($chatId,$erMess);
                                return 0;
                            } else {
                                // send for furtther processing
                                $waitmsg = "Analyzing, Please wait a few moments...";
                                $this->sendMessage($chatId,$waitmsg);
                                $data = array('article'=>$message);
                                $this->sendtoRating($chatId,$data);
                                return 1;
                            }
                        }

                        public function askHelp($chatId,$senderName) {
                            $helpmessage = "Hie ".$senderName.", I am Edith 👩🏾‍💼 \n\nI can help you verify if the news you are recieving on social media is real or fake.\n\nTo do this , all you have to do is send or forward the news article to this chat and i'll send you an answer in a few moments.\n\nYes, its that simple! 😊 but if you have futher questions please visit our website www.edithnews.com/help or send an email to mareberao@gmail.com";
                            $this->sendMessage($chatId,$helpmessage);
                        }

                        public function sendtoRating($chatId,$data){
                            $url = 'https://ultimate-flare-271515.appspot.com/checksimilarity/';
                            if(is_array($data)){ $data = json_encode($data);}
                            $options = stream_context_create(['http' => [
                            'method'  => 'POST',
                            'header'  => 'Content-type: application/json',
                            'content' => $data]]);
                            $response = file_get_contents($url,false,$options);
                            // $array = $this->object_to_array($response);
                            $this->sendMessage($chatId,$response);
                            return 200;
                        }

                        public function object_to_array($data)
                            {
                                if (is_array($data) || is_object($data))
                                {
                                    $result = array();
                                    foreach ($data as $key => $value)
                                    {
                                        $result[$key] = object_to_array($value);
                                    }
                                    return $result;
                                }
                                return $data;
                            }


                        public function sendMessage($chatId, $text){
                        $data = array('chatId'=>$chatId,'body'=>$text);
                        $this->sendRequest('message',$data);}
                        
                        public function sendRequest($method,$data){
                        $url = $this->APIurl.$method.'?token='.$this->token;
                        if(is_array($data)){ $data = json_encode($data);}
                        $options = stream_context_create(['http' => [
                        'method'  => 'POST',
                        'header'  => 'Content-type: application/json',
                        'content' => $data]]);
                        $response = file_get_contents($url,false,$options);
                        file_put_contents('requests.log',$response.PHP_EOL,FILE_APPEND);}}
                        //execute the class when this file is requested by the instance
                        new whatsAppBot();}
                    ?>