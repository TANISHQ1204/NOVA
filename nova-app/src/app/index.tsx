import {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';

export default function HomeScreen(){
  const[message, setMessage]=useState('');
  return(
    <View style={styles.container}>
      <Text style={styles.title}>NOVA</Text>
      <TextInput
      style={styles.input}
      placeholder='Type a message...'
      value={message}
      onChangeText={setMessage}
      />
      <Button title='Send' onPress={()=>console.log(message)}/>
    </View>
  );
}

const styles=StyleSheet.create({
  container:{
    flex:1,
    justifyContent:'center',
    padding:20,
    backgroundColor:'#0a0a0a',
  },
  title:{
    fontSize:32,
    color:'#00ffff',
    textAlign:'center',
    marginBottom:20,
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