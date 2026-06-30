import {useEffect, useState, useRef} from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';

const NOVA_IP='192.168.1.8';

export default function HomeScreen(){
  const[message, setMessage]=useState('');
  const[chatLog, setChatLog]=useState<string[]>([]);
  const ws=useRef<WebSocket|null>(null);

  useEffect(()=>{
    ws.current=new WebSocket(`ws://${NOVA_IP}:8000/ws`);

    ws.current.onopen=()=>{
      console.log('Connected to NOVA');
    };

    ws.current.onmessage=(event)=>{
      setChatLog((prev)=>[...prev, `NOVA: ${event.data}`]);
    };

    ws.current.onerror=(error)=>{
      console.log('WebSocket error:',error);
    };

    return()=>{
      ws.current?.close();
    };
  },[]);

  const sendMessage=()=>{
    if(ws.current&&message.trim()){
      ws.current?.send(message);
      setChatLog((prev)=>[...prev, `You: ${message}`]);
      setMessage('');
    }
  };

  return(
    <View style={styles.container}>
      <Text style={styles.title}>NOVA</Text>
      <ScrollView style={styles.chatBox}>
        {chatLog.map((line, index)=>(
          <Text key={index} style={styles.chatLine}>{line}</Text>
        ))}
      </ScrollView>
      <TextInput
      style={styles.input}
      placeholder='Type a message...'
      value={message}
      onChangeText={setMessage}
      />
      <Button title='Send' onPress={sendMessage}/>
    </View>
  );
}

const styles=StyleSheet.create({
  container:{
    flex:1,
    padding:20,
    backgroundColor:'#0a0a0a',
    paddingTop:60,
  },
  title:{
    fontSize:32,
    color:'#00ffff',
    textAlign:'center',
    marginBottom:20,
  },
  chatBox:{
    flex:1,
    marginBottom:12,
  },
  chatLine:{
    color:'#fff',
    marginBottom:6,
  },
  input:{
    borderWidth:1,
    borderColor:'#00ffff',
    borderRadius:8,
    padding:12,
    color:'#fff',
    marginBottom:12,
  },
});