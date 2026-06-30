import {useEffect, useState, useRef} from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';

const NOVA_IP='192.168.1.8';

export default function HomeScreen(){
  const[message, setMessage]=useState('');
  const[chatLog, setChatLog]=useState<string[]>([]);
  const[connected, setConnected]=useState(false);
  const[thinking, setThinking]=useState(false);
  const ws=useRef<WebSocket|null>(null);
  const scrollRef=useRef<ScrollView>(null);

  useEffect(()=>{
    ws.current=new WebSocket(`ws://${NOVA_IP}:8000/ws`);

    ws.current.onopen=()=>{
      setConnected(true);
    };

    ws.current.onmessage=(event)=>{
      setThinking(false);
      setChatLog((prev)=>[...prev, `NOVA: ${event.data}`]);
    };

    ws.current.onerror=(error)=>{
      setConnected(false);
    };

    ws.current.onclose=()=>{
      setConnected(false);
    };

    return()=>{
      ws.current?.close();
    };
  },[]);

  useEffect(()=>{
    scrollRef.current?.scrollToEnd({animated:true});
  }, [chatLog]);

  const sendMessage=()=>{
    if(ws.current&&message.trim()){
      ws.current?.send(message);
      setChatLog((prev)=>[...prev, `You: ${message}`]);
      setThinking(true);
      setMessage('');
    }
  };

  return(
    <View style={styles.container}>
      <Text style={styles.title}>NOVA</Text>
      <Text style={styles.status}>
        {connected ? '\u25CF Connected' : '\u25CB Disconnected'}
      </Text>
      <ScrollView ref={scrollRef} style={styles.chatBox}>
        {chatLog.map((line, index)=>(
          <Text key={index} style={styles.chatLine}>{line}</Text>
        ))}
        {thinking&&<Text style={styles.thinking}>NOVA is thinking...</Text>}
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
    marginBottom:4,
  },
  chatBox:{
    flex:1,
    marginBottom:12,
  },
  status:{
    color:'#888',
    textAlign:'center',
    marginBottom:16,
    fontSize:12,
  },
  chatLine:{
    color:'#fff',
    marginBottom:6,
  },
  thinking:{
    color:'#00ffff',
    fontStyle:'italic',
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