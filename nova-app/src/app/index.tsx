import {useEffect, useState, useRef} from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
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
        <View style={styles.core} />
        <Text style={styles.status}>LOADING</Text>
      </View>
    );
  }

  if(!novaIp){
    return (
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.bootBlock}>
          <Text style={styles.title}>NOVA<Text style={styles.titleAccent}>_</Text></Text>
          <Text style={styles.status}>ENTER NOVA'S IP ADDRESS</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. 192.168.1.8"
            placeholderTextColor="#454E56"
            value={ipInput}
            onChangeText={setIpInput}
            autoCapitalize="none"
            keyboardType="numeric"
          />
          <TouchableOpacity style={styles.primaryButton} onPress={saveIp}>
            <Text style={styles.primaryButtonText}>CONNECT</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    );
  }

  return(
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.header}>
        <Text style={styles.title}>NOVA<Text style={styles.titleAccent}>_</Text>CONSOLE</Text>
        <View style={styles.headerRow}>
          <View style={styles.connChip}>
            <View style={[styles.dot, connected ? styles.dotOnline : styles.dotOffline]} />
            <Text style={styles.connLabel}>{connected ? 'ONLINE' : 'OFFLINE'}</Text>
          </View>
          <TouchableOpacity onPress={changeIp}>
            <Text style={styles.changeIpText}>CHANGE IP</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView
        ref={scrollRef}
        style={styles.chatBox}
        contentContainerStyle={styles.chatContent}
      >
        {chatLog.length === 0 && !thinking && (
          <View style={styles.emptyBox}>
            <Text style={styles.emptyText}>No messages yet. Say something to NOVA.</Text>
          </View>
        )}
        {chatLog.map((line, index)=>{
          const isNova = line.startsWith('NOVA:');
          const text = isNova ? line.replace('NOVA:','').trim() : line.replace('You:','').trim();
          return (
            <View
              key={index}
              style={[styles.bubble, isNova ? styles.bubbleNova : styles.bubbleUser]}
            >
              <Text style={[styles.bubbleHead, isNova ? styles.bubbleHeadNova : styles.bubbleHeadUser]}>
                {isNova ? 'NOVA' : 'YOU'}
              </Text>
              <Text style={styles.bubbleText}>{text}</Text>
            </View>
          );
        })}
        {thinking && (
          <View style={[styles.bubble, styles.bubbleNova, styles.bubblePending]}>
            <Text style={[styles.bubbleHead, styles.bubbleHeadPending]}>NOVA · THINKING</Text>
            <Text style={styles.bubbleText}>...</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.inputRow}>
        <TextInput
          style={styles.messageInput}
          placeholder="Type a message..."
          placeholderTextColor="#454E56"
          value={message}
          onChangeText={setMessage}
          onSubmitEditing={sendMessage}
          returnKeyType="send"
        />
        <TouchableOpacity style={styles.sendButton} onPress={sendMessage}>
          <Text style={styles.sendButtonText}>SEND</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const COLORS = {
  bgVoid: '#0A0D10',
  panel: '#12171C',
  panelRaised: '#161D23',
  line: '#232B32',
  lineBright: '#324049',
  textPrimary: '#DCE4E8',
  textMuted: '#6B7680',
  textDim: '#454E56',
  coreTeal: '#45D9C0',
  coreTealDim: 'rgba(69,217,192,0.14)',
  signalAmber: '#FF9D4D',
  danger: '#FF5D5D',
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgVoid,
    paddingHorizontal: 18,
    paddingTop: 56,
  },
  bootBlock: {
    flex: 1,
    justifyContent: 'center',
  },
  core: {
    alignSelf: 'center',
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: COLORS.coreTeal,
    marginBottom: 16,
  },
  header: {
    marginBottom: 14,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.line,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 10,
  },
  title: {
    fontSize: 22,
    color: COLORS.textPrimary,
    letterSpacing: 3,
    fontWeight: '700',
  },
  titleAccent: {
    color: COLORS.coreTeal,
  },
  status: {
    color: COLORS.textMuted,
    textAlign: 'center',
    marginBottom: 20,
    fontSize: 11,
    letterSpacing: 2,
    marginTop: 10,
  },
  connChip: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    marginRight: 7,
  },
  dotOnline: {
    backgroundColor: COLORS.coreTeal,
  },
  dotOffline: {
    backgroundColor: COLORS.danger,
  },
  connLabel: {
    color: COLORS.textMuted,
    fontSize: 11,
    letterSpacing: 1.5,
  },
  changeIpText: {
    color: COLORS.textDim,
    fontSize: 11,
    letterSpacing: 1,
    textDecorationLine: 'underline',
  },
  chatBox: {
    flex: 1,
  },
  chatContent: {
    paddingBottom: 12,
  },
  emptyBox: {
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: COLORS.line,
    borderRadius: 6,
    padding: 24,
    marginTop: 20,
  },
  emptyText: {
    color: COLORS.textDim,
    fontSize: 12,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  bubble: {
    borderRadius: 6,
    padding: 12,
    marginBottom: 10,
    maxWidth: '86%',
    borderWidth: 1,
  },
  bubbleUser: {
    alignSelf: 'flex-end',
    backgroundColor: COLORS.panelRaised,
    borderColor: COLORS.line,
  },
  bubbleNova: {
    alignSelf: 'flex-start',
    backgroundColor: COLORS.coreTealDim,
    borderColor: 'rgba(69,217,192,0.3)',
  },
  bubblePending: {
    borderStyle: 'dashed',
    opacity: 0.85,
  },
  bubbleHead: {
    fontSize: 10,
    letterSpacing: 1.5,
    marginBottom: 4,
  },
  bubbleHeadUser: {
    color: COLORS.textMuted,
    textAlign: 'right',
  },
  bubbleHeadNova: {
    color: COLORS.coreTeal,
  },
  bubbleHeadPending: {
    color: COLORS.signalAmber,
  },
  bubbleText: {
    color: COLORS.textPrimary,
    fontSize: 14,
    lineHeight: 20,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 20,
    gap: 8,
  },
  messageInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 6,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: COLORS.textPrimary,
    backgroundColor: COLORS.panelRaised,
    fontSize: 14,
  },
  input: {
    borderWidth: 1,
    borderColor: COLORS.line,
    borderRadius: 6,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: COLORS.textPrimary,
    backgroundColor: COLORS.panelRaised,
    fontSize: 14,
    marginBottom: 16,
  },
  sendButton: {
    backgroundColor: COLORS.coreTealDim,
    borderWidth: 1,
    borderColor: COLORS.coreTeal,
    borderRadius: 6,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  sendButtonText: {
    color: COLORS.coreTeal,
    fontSize: 12,
    letterSpacing: 1,
    fontWeight: '600',
  },
  primaryButton: {
    backgroundColor: COLORS.coreTealDim,
    borderWidth: 1,
    borderColor: COLORS.coreTeal,
    borderRadius: 6,
    paddingVertical: 14,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: COLORS.coreTeal,
    fontSize: 13,
    letterSpacing: 1.5,
    fontWeight: '600',
  },
});