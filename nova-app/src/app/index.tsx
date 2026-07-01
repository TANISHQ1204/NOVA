import {useEffect, useState, useRef} from 'react';
import { View, Text, TextInput, Button, StyleSheet, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function HomeScreen(){
  const[message, setMessage]=useState('');
  const[chatLog, setChatLog]=useState<string[]>([]);
  const[connected, setConnected]=useState(false);
  const[thinking, setThinking]=useState(false);
  const ws=useRef<WebSocket|null>(null);
  const scrollRef=useRef<ScrollView>(null);

  const[novaIp, setNovaIp]=useState<string|null>(null);
  const[ipInput, setIpInput]=useState('');
  const[checkingStorage, setCheckingStorage]=useState(true);

  useEffect(()=>{
    AsyncStorage.getItem('nova_ip').then((saved)=>{
      if(saved) setNovaIp(saved);
      setCheckingStorage(false);
    });
  },[]);

  useEffect(()=>{
    if(!novaIp) return;

    function connect(){
      ws.current=new WebSocket(`ws://${novaIp}:8000/ws`);

      ws.current.onopen=()=>{
        setConnected(true);
      };

      ws.current.onmessage=(event)=>{
        setThinking(false);
        setChatLog((prev)=>[...prev, `NOVA: ${event.data}`]);
      };

      ws.current.onerror=()=>{
        setConnected(false);
      };

      ws.current.onclose=()=>{
        setConnected(false);
        setTimeout(connect,3000);
      };
    }

    connect();

    return()=>{
      ws.current?.close();
    };
  },[novaIp]);

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

  const saveIp=()=>{
    if(ipInput.trim()){
      AsyncStorage.setItem('nova_ip', ipInput.trim());
      setNovaIp(ipInput.trim());
    }
  };

  const changeIp = () => {
    AsyncStorage.removeItem('nova_ip');
    setNovaIp(null);
    setIpInput('');
  };

  if(checkingStorage){
  return (
    <View style={styles.container}>
      <Text style={styles.status}>Loading...</Text>
    </View>
  );
}

if(!novaIp){
  return (
    <View style={styles.container}>
      <Text style={styles.title}>NOVA</Text>
      <Text style={styles.status}>Enter NOVA's IP address</Text>
      <TextInput
        style={styles.input}
        placeholder='e.g. 192.168.1.8'
        value={ipInput}
        onChangeText={setIpInput}
        autoCapitalize='none'
        keyboardType='numeric'
      />
      <Button title='Connect' onPress={saveIp}/>
    </View>
  );
}

  return(
    <View style={styles.container}>
      <Text style={styles.title}>NOVA</Text>
      <Text style={styles.status}>
        {connected ? '\u25CF Connected' : '\u25CB Disconnected'}
      </Text>
      <Button title='Change IP' onPress={changeIp}/>
      <ScrollView ref={scrollRef} style={styles.chatBox}>
        {chatLog.map((line, index)=>(
          <Text key={index} style={line.startsWith('NOVA:')?styles.novaLine:styles.chatLine}>{line}</Text>
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

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#050505',
    paddingTop: 60,
  },
  title: {
    fontSize: 34,
    color: '#00ffff',
    textAlign: 'center',
    marginBottom: 4,
    letterSpacing: 8,
    fontWeight: '900',
    textShadowColor: '#00ffff',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 15,
  },
  status: {
    color: '#888',
    textAlign: 'center',
    marginBottom: 16,
    fontSize: 11,
    letterSpacing: 2,
  },
  chatBox: {
    flex: 1,
    marginBottom: 12,
  },
  chatLine: {
    color: '#ffffff',
    marginBottom: 10,
    padding: 10,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 8,
    borderLeftWidth: 2,
    borderLeftColor: '#ffffff',
  },
  novaLine: {
    color: '#00ffff',
    marginBottom: 10,
    padding: 10,
    backgroundColor: 'rgba(0,255,255,0.05)',
    borderRadius: 8,
    borderLeftWidth: 2,
    borderLeftColor: '#00ffff',
  },
  thinking: {
    color: '#ff9933',
    fontStyle: 'italic',
    marginBottom: 6,
    fontSize: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#00ffff',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    marginBottom: 12,
    backgroundColor: 'rgba(0,255,255,0.03)',
  },
});