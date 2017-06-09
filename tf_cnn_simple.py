from __future__ import print_function, division, absolute_import
import tensorflow as tf
import utils

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W, stride_size=1):
    return tf.nn.conv2d(x, W, strides=[1, stride_size, stride_size, 1], padding='SAME')

def max_pool_2x2(x, pool_size=2, stride_size=2):
    return tf.nn.max_pool(x, ksize=[1, pool_size, pool_size, 1], strides=[1, stride_size, stride_size, 1], padding='SAME')

def main_cnn(_):
    x = tf.placeholder(tf.float32, [None, 196, 196, 3])
    x_image = tf.reshape(x, [-1, 196, 196, 3])
    y_ = tf.placeholder(tf.float32, [None, 2])

    W_conv1 = weight_variable([5, 5, 3, 32])
    b_conv1 = bias_variable([32])
    
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([49 * 49 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 49*49*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    W_fc2 = weight_variable([1024, 2])
    b_fc2 = bias_variable([2])

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    sess = tf.InteractiveSession()

    sess.run(tf.global_variables_initializer())

    for i in range(20):
        batch_files = utils.all_files()
        batch_x = [utils.get_image(batch_file) for batch_file in batch_files]
        batch_y = [[0,1] for batch_file in batch_files]

        print(i)

        if i%10 == 0:
            train_accuracy = accuracy.eval(feed_dict={
                x: batch_x, y_: batch_y, keep_prob: 1.0})
            print("step %d, training accuracy %g"%(i, train_accuracy))
        train_step.run(feed_dict={x_image: batch_x, y_: batch_y, keep_prob: 0.5})

    #print("test accuracy %g"%accuracy.eval(feed_dict={
    #    x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))

if __name__ == "__main__":
    tf.app.run(main=main_cnn, argv=None)
