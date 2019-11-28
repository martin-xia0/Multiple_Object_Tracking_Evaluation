## Welcome to SOTPU

Object location & pose tracking benchmark for video surveillance<br />

Our challenge includes two kinds of tracking, MOT and PoseTrack. You can choose either or both.

Our basic goal is to provide a human tracking benchmark in the surveillance videos.<br />

Based on this benchmark, we wish to advance the state of art in the human recognition and tracking. We provide a huge amount of annotated data under surveillance videos. 

## What do we provide?

1. A large dataset, which includes a bulk of annotated video surveillance <br />
2. A challenging system, you can create your personal account and submit your training results, we will immediately give performance results<br />
3. An evaluation framework, which evaluates your model <br />
4. A video composer, when you submit your result, you will get your own video based on your training results<br />

## What can you do ?

1. You can download the surveillance video dataset, use those data to train your model.<br />
2. You can create a tracker and submit your results. You will receive the performance evaluation of your model. <br />


## FAQ

#### What qualifications do I need to apply for an account?

1. You need fill in your affliation for registration, so you need to be in a university, lab group or cooperation. <br />
2. After you fill in the basic information, we will send you an activation email to verify the email address authenticity.<br />
3. You can activate your account by clicking the link in email, our staff will then make a human review (which will take 1~3 days) and enable your account. <br />
4. After human review, you will recieve a notification email, then you can use your account.  <br />

#### How can I join the challenge and create a tracker?

1. You can join one challenge by creating a tracker. You can create trackers in your home page, you need to fill in some important information about the tracker, which includes challenges, runtime, hardware ect.  <br />
2. After filling out all the information, upload your training result and submit the tracker. <br />
3. Our server will immediately read your result file and evaluate the performance by our evaluation metrics, and return the evaluation result. You can see it on "result" page. <br />
4. Meanwhile Our server will use your result to compose the annotated frames and videos, which will be displayed on your tracker detail page. <br />

#### What user rules should I obey?

1. You must only have one account, multiple accounts of one person is not allowed. <br />
2. Please fill in your authentic organization and the  institutional email when you create your account. For example,  your university, group or  cooperation, etc. <br />
3. If there’s any violation of the account rules, your accounts will be desabled. <br />
4. If you have problems about your account, please send an email to "xiazexin@sjtu.edu.cn" <br />

#### How about the submission rules?

1. You only need to submit result of test videos. <br />
2. You can submit no more than 3 times in one challenge, you need to wait at least 3 days to re-submit your results. <br />
3. When you submit results in your website background, you need to create a tracker, then fill in the information and upload the result package. <br />
4. If there’s any violation of the submission rules, your tracker will be canceled. <br />

#### What's the file format should I use?

    Each challenge includes multiple videos, you have to train your model and get the result of each test video( don't submit result of training videos). You need to arrage your result in txt file format, for each test video, the file name of the corresponding video is <video_id>.txt，wrong filename will cause evaluation error.<br />

    Please organize all the result txt into one zip file, submit this package when you create a tracker.<br />

    The file format is shown below:<br />

1. Each txt represents one video and includes many frames, each frame has several objects.<br />
2. MOT challenge:<br />
   frame-id, obj-id, x, w, y, h, control-num <br />
   Frame id: frame-id is the id of each frame, starts counting at 0 <br />
   Object id: obj-id is the id of the object being tracked<br />
   x, w, y, h: These four parameters represent a rectangle<br />
   Control number: control-num is set to meet new classification requirements, now we set it as 1 as default value<br />
3. POSE TRACK challenge:<br />
   frame-id, obj-id, skeleton points(14 points), control-num <br />
   Frame id: frame-id is the id of each frame, starts counting at 0.<br />
   Object id: obj-id is the id of the object being tracked.<br />
   Skeleton points(14 points): skeleton points includes 28 parameters, represent 14 skeleton points of a human<br />
   Control number: control-num is set to meet new classification requirements, now we set it as 1 as default value
